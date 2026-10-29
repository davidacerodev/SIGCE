import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.integrations.storage import get_storage
from app.models import Notebook, Source, User
from app.schemas.api import NotebookIn, NotebookOut, NotebookPatch


def get_owned(db: Session, user: User, notebook_id: uuid.UUID) -> Notebook:
    nb = db.scalar(select(Notebook).where(Notebook.id == notebook_id, Notebook.owner_id == user.id))
    if not nb:  # también para cuadernos ajenos: no se revela su existencia
        raise NotFoundError("Cuaderno no encontrado.")
    return nb


def touch(nb: Notebook) -> None:
    nb.updated_at = datetime.now(timezone.utc)


def _out(db: Session, nb: Notebook) -> NotebookOut:
    count = db.scalar(select(func.count()).select_from(Source).where(Source.notebook_id == nb.id)) or 0
    return NotebookOut.model_validate(nb).model_copy(update={"source_count": count})


def list_notebooks(db: Session, user: User, limit: int, offset: int) -> list[NotebookOut]:
    rows = db.scalars(
        select(Notebook).where(Notebook.owner_id == user.id).order_by(Notebook.updated_at.desc()).limit(limit).offset(offset)
    ).all()
    return [_out(db, nb) for nb in rows]


def create(db: Session, user: User, data: NotebookIn) -> NotebookOut:
    nb = Notebook(owner_id=user.id, title=data.title.strip(), description=data.description)
    db.add(nb)
    db.commit()
    return _out(db, nb)


def update(db: Session, user: User, notebook_id: uuid.UUID, data: NotebookPatch) -> NotebookOut:
    nb = get_owned(db, user, notebook_id)
    if data.title is not None:
        nb.title = data.title.strip()
    if data.description is not None:
        nb.description = data.description
    db.commit()
    db.refresh(nb)
    return _out(db, nb)


def delete(db: Session, user: User, notebook_id: uuid.UUID) -> None:
    nb = get_owned(db, user, notebook_id)
    keys = [s.storage_key for s in nb.sources if s.storage_key]
    db.delete(nb)
    db.commit()
    storage = get_storage()
    for key in keys:
        storage.delete(key)
