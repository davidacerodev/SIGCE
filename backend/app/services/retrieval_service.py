import re
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ValidationFailed
from app.integrations.ai.base import RetrievedChunk
from app.models import DocumentChunk, Source
from app.models.enums import SourceStatus

_WORD = re.compile(r"\w{3,}", re.UNICODE)


def _ready_chunks(db: Session, notebook_id: uuid.UUID, source_ids: list[uuid.UUID] | None):
    query = (
        select(DocumentChunk, Source)
        .join(Source, DocumentChunk.source_id == Source.id)
        .where(Source.notebook_id == notebook_id, Source.status == SourceStatus.READY)
        .order_by(Source.created_at, DocumentChunk.position)
    )
    if source_ids is not None:
        query = query.where(Source.id.in_(source_ids))
    rows = db.execute(query).all()
    if not rows:
        raise ValidationFailed("Selecciona al menos una fuente lista para consultar.")
    return rows


def _to_retrieved(chunk: DocumentChunk, src: Source) -> RetrievedChunk:
    return RetrievedChunk(str(src.id), src.name, chunk.position, chunk.content)


def retrieve(db: Session, notebook_id: uuid.UUID, question: str, source_ids: list[uuid.UUID] | None, k: int = 5) -> list[RetrievedChunk]:
    """Recuperación por coincidencia de palabras. No es búsqueda semántica: aún no hay embeddings."""
    terms = {w.lower() for w in _WORD.findall(question)}
    scored = []
    for chunk, src in _ready_chunks(db, notebook_id, source_ids):
        words = [w.lower() for w in _WORD.findall(chunk.content)]
        score = sum(1 for w in words if w in terms)
        if score:
            scored.append((score, _to_retrieved(chunk, src)))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:k]]


def leading_chunks(db: Session, notebook_id: uuid.UUID, source_ids: list[uuid.UUID] | None, limit: int = 8) -> list[RetrievedChunk]:
    return [_to_retrieved(c, s) for c, s in _ready_chunks(db, notebook_id, source_ids)[:limit]]
