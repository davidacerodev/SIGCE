import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.integrations.ai import get_ai_provider
from app.models import GeneratedArtifact, Notebook, Source
from app.models.enums import ArtifactStatus, ArtifactType
from app.services import retrieval_service

logger = logging.getLogger(__name__)

TITLES = {
    ArtifactType.SUMMARY: "Resumen", ArtifactType.FAQ: "Preguntas frecuentes", ArtifactType.STUDY_GUIDE: "Guía de estudio",
    ArtifactType.FLASHCARDS: "Tarjetas de memoria", ArtifactType.QUIZ: "Cuestionario", ArtifactType.MIND_MAP: "Mapa mental",
}


def generate(db: Session, nb: Notebook, type_: ArtifactType, source_ids: list[uuid.UUID] | None) -> GeneratedArtifact:
    chunks = retrieval_service.leading_chunks(db, nb.id, source_ids)
    used = {c.source_id for c in chunks}
    artifact = GeneratedArtifact(notebook_id=nb.id, type=type_, title=TITLES[type_], status=ArtifactStatus.GENERATING)
    artifact.sources = list(db.scalars(select(Source).where(Source.id.in_([uuid.UUID(i) for i in used]))))
    db.add(artifact)
    db.commit()
    try:
        artifact.content = get_ai_provider().generate(type_.value, chunks)
        artifact.status = ArtifactStatus.READY
    except Exception as exc:
        logger.exception("Fallo al generar recurso %s", artifact.id)
        artifact.status = ArtifactStatus.FAILED
        artifact.error_message = f"No se pudo generar el recurso: {type(exc).__name__}"
    db.commit()
    return artifact


def get_artifact(db: Session, nb: Notebook, artifact_id: uuid.UUID) -> GeneratedArtifact:
    art = db.scalar(select(GeneratedArtifact).where(GeneratedArtifact.id == artifact_id, GeneratedArtifact.notebook_id == nb.id))
    if not art:
        raise NotFoundError("Recurso no encontrado.")
    return art


def list_artifacts(db: Session, nb: Notebook) -> list[GeneratedArtifact]:
    return list(db.scalars(select(GeneratedArtifact).where(GeneratedArtifact.notebook_id == nb.id).order_by(GeneratedArtifact.created_at.desc())))
