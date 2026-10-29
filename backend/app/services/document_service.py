import hashlib
import logging
import uuid
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import Conflict, NotFoundError, ValidationFailed
from app.db.session import SessionLocal
from app.integrations.storage import get_storage
from app.models import DocumentChunk, Notebook, Source
from app.models.enums import SourceStatus, SourceType
from app.services import notebook_service

logger = logging.getLogger(__name__)

ALLOWED = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf"}
CHUNK_SIZE = 1000


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Agrupa párrafos hasta ~size caracteres; los párrafos más largos se parten."""
    chunks, current = [], ""
    for para in (p.strip() for p in text.split("\n\n")):
        if not para:
            continue
        while len(para) > size:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:size])
            para = para[size:]
        if current and len(current) + len(para) + 2 > size:
            chunks.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current)
    return chunks


def _validate_upload(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED:
        raise ValidationFailed("Formato no admitido. Usa PDF, TXT o Markdown.")
    if not data:
        raise ValidationFailed("El archivo está vacío.")
    if len(data) > get_settings().max_upload_mb * 1024 * 1024:
        raise ValidationFailed(f"El archivo supera el límite de {get_settings().max_upload_mb} MB.")
    if ext == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise ValidationFailed("El contenido no corresponde a un PDF válido.")
    else:
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationFailed("El archivo de texto debe estar codificado en UTF-8.") from None
        if b"\x00" in data:
            raise ValidationFailed("El archivo contiene datos binarios.")
    return ext


def _create_source(db: Session, nb: Notebook, *, type_: SourceType, name: str, ext: str, data: bytes) -> Source:
    digest = hashlib.sha256(data).hexdigest()
    if db.scalar(select(Source.id).where(Source.notebook_id == nb.id, Source.content_hash == digest)):
        raise Conflict("Esta fuente ya existe en el cuaderno.")
    key = f"{uuid.uuid4().hex}{ext}"
    storage = get_storage()
    storage.save(key, data)
    source = Source(
        notebook_id=nb.id, type=type_, name=name[:255], mime_type=ALLOWED[ext], size_bytes=len(data),
        storage_key=key, content_hash=digest, status=SourceStatus.PENDING,
    )
    db.add(source)
    notebook_service.touch(nb)
    try:
        db.commit()
    except IntegrityError:  # carrera entre dos cargas idénticas
        db.rollback()
        storage.delete(key)
        raise Conflict("Esta fuente ya existe en el cuaderno.") from None
    return source


def create_file_source(db: Session, nb: Notebook, filename: str, data: bytes) -> Source:
    ext = _validate_upload(filename, data)
    # Solo se conserva el nombre base: se descarta cualquier ruta enviada por el cliente.
    return _create_source(db, nb, type_=SourceType.FILE, name=Path(filename).name, ext=ext, data=data)


def create_text_source(db: Session, nb: Notebook, name: str, content: str) -> Source:
    data = content.encode("utf-8")
    _validate_upload("texto.txt", data)
    return _create_source(db, nb, type_=SourceType.TEXT, name=name.strip(), ext=".txt", data=data)


def get_source(db: Session, nb: Notebook, source_id: uuid.UUID) -> Source:
    src = db.scalar(select(Source).where(Source.id == source_id, Source.notebook_id == nb.id))
    if not src:
        raise NotFoundError("Fuente no encontrada.")
    return src


def delete_source(db: Session, nb: Notebook, source_id: uuid.UUID) -> None:
    src = get_source(db, nb, source_id)
    key = src.storage_key
    db.delete(src)
    db.commit()
    if key:
        get_storage().delete(key)


def _extract_text(src: Source, data: bytes) -> str:
    if src.storage_key and src.storage_key.endswith(".pdf"):
        import io

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)
    return data.decode("utf-8")


def process_source(source_id: uuid.UUID, session_factory: Callable[[], Session] = SessionLocal) -> None:
    """Extrae texto y genera fragmentos. Pensado para ejecutarse en segundo plano."""
    db = session_factory()
    try:
        src = db.get(Source, source_id)
        if not src or src.status != SourceStatus.PENDING:
            return
        src.status = SourceStatus.PROCESSING
        db.commit()
        try:
            text = _extract_text(src, get_storage().read(src.storage_key))
            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("El documento no contiene texto extraíble.")
            db.add_all(DocumentChunk(source_id=src.id, position=i, content=c) for i, c in enumerate(chunks))
            src.status = SourceStatus.READY
            src.error_message = None
        except Exception as exc:  # el fallo se registra en la fuente, no en la petición
            logger.warning("Fallo al procesar fuente %s: %s", source_id, exc)
            db.rollback()
            src = db.get(Source, source_id)
            src.status = SourceStatus.FAILED
            src.error_message = "No se pudo extraer el texto del documento."
            if isinstance(exc, ValueError):
                src.error_message = str(exc)
        db.commit()
    finally:
        db.close()
