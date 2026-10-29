import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import ChatIn, ChatOut, MessageOut
from app.services import ai_service, notebook_service

router = APIRouter(prefix="/notebooks/{notebook_id}", tags=["chat"])


@router.get("/messages", response_model=list[MessageOut])
def messages(notebook_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ai_service.list_messages(db, notebook_service.get_owned(db, user, notebook_id))


@router.post("/chat", response_model=ChatOut)
def chat(notebook_id: uuid.UUID, data: ChatIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nb = notebook_service.get_owned(db, user, notebook_id)
    user_msg, assistant_msg = ai_service.chat(db, nb, data.message.strip(), data.source_ids)
    return ChatOut(user_message=user_msg, assistant_message=assistant_msg)
