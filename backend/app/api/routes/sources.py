import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.errors import ValidationFailed
from app.db.session import get_db
from app.models import Source, User
from app.schemas.api import SourceOut, TextSourceIn
from app.services import document_service as docs
from app.services import notebook_service

router = APIRouter(prefix="/notebooks/{notebook_id}/sources", tags=["sources"])


@router.get("", response_model=list[SourceOut])
def list_sources(notebook_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    return db.scalars(select(Source).where(Source.notebook_id == nb.id).order_by(Source.created_at)).all()


@router.post("/text", response_model=SourceOut, status_code=201)
def add_text(notebook_id: uuid.UUID, data: TextSourceIn, tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    src = docs.create_text_source(db, nb, data.name, data.content)
    tasks.add_task(docs.process_source, src.id)
    return src


@router.post("/upload", response_model=SourceOut, status_code=201)
async def upload(notebook_id: uuid.UUID, tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)  # nunca se lee más del límite
    if len(data) > limit:
        raise ValidationFailed(f"El archivo supera el límite de {get_settings().max_upload_mb} MB.")
    src = docs.create_file_source(db, nb, file.filename or "archivo", data)
    tasks.add_task(docs.process_source, src.id)
    return src


@router.get("/{source_id}", response_model=SourceOut)
def get_source(notebook_id: uuid.UUID, source_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return docs.get_source(db, notebook_service.get_owned(db, user, notebook_id), source_id)


@router.delete("/{source_id}", status_code=204)
def delete_source(notebook_id: uuid.UUID, source_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    docs.delete_source(db, notebook_service.get_owned(db, user, notebook_id), source_id)
    return Response(status_code=204)
