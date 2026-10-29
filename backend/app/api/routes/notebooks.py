import uuid

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import NotebookIn, NotebookOut, NotebookPatch
from app.services import notebook_service as svc

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.get("", response_model=list[NotebookOut])
def list_notebooks(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return svc.list_notebooks(db, user, limit, offset)


@router.post("", response_model=NotebookOut, status_code=201)
def create_notebook(data: NotebookIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return svc.create(db, user, data)


@router.get("/{notebook_id}", response_model=NotebookOut)
def get_notebook(notebook_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return svc._out(db, svc.get_owned(db, user, notebook_id))


@router.patch("/{notebook_id}", response_model=NotebookOut)
def update_notebook(notebook_id: uuid.UUID, data: NotebookPatch, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return svc.update(db, user, notebook_id, data)


@router.delete("/{notebook_id}", status_code=204)
def delete_notebook(notebook_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    svc.delete(db, user, notebook_id)
    return Response(status_code=204)
