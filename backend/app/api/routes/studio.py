import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import ArtifactIn, ArtifactOut
from app.services import notebook_service, studio_service

router = APIRouter(prefix="/notebooks/{notebook_id}/artifacts", tags=["studio"])


@router.get("", response_model=list[ArtifactOut])
def list_artifacts(notebook_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return studio_service.list_artifacts(db, notebook_service.get_owned(db, user, notebook_id))


@router.post("", response_model=ArtifactOut, status_code=201)
def create_artifact(notebook_id: uuid.UUID, data: ArtifactIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    return studio_service.generate(db, nb, data.type, data.source_ids)


@router.get("/{artifact_id}", response_model=ArtifactOut)
def get_artifact(notebook_id: uuid.UUID, artifact_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return studio_service.get_artifact(db, notebook_service.get_owned(db, user, notebook_id), artifact_id)


@router.delete("/{artifact_id}", status_code=204)
def delete_artifact(notebook_id: uuid.UUID, artifact_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    db.delete(studio_service.get_artifact(db, nb, artifact_id))
    db.commit()
    return Response(status_code=204)
