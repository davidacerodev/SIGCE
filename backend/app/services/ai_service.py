import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.ai import get_ai_provider
from app.models import Conversation, Message, Notebook
from app.models.enums import MessageRole
from app.services import notebook_service, retrieval_service


def get_conversation(db: Session, nb: Notebook) -> Conversation:
    conv = db.scalar(select(Conversation).where(Conversation.notebook_id == nb.id).order_by(Conversation.created_at))
    if not conv:
        conv = Conversation(notebook_id=nb.id)
        db.add(conv)
        db.commit()
    return conv


def list_messages(db: Session, nb: Notebook) -> list[Message]:
    conv = get_conversation(db, nb)
    return list(db.scalars(select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at, Message.role.desc())))


def chat(db: Session, nb: Notebook, text: str, source_ids: list[uuid.UUID] | None) -> tuple[Message, Message]:
    chunks = retrieval_service.retrieve(db, nb.id, text, source_ids)  # valida que haya fuentes listas
    result = get_ai_provider().answer(text, chunks)
    conv = get_conversation(db, nb)
    user_msg = Message(conversation_id=conv.id, role=MessageRole.USER, content=text)
    assistant_msg = Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content=result.text, citations=result.citations)
    db.add_all([user_msg, assistant_msg])
    notebook_service.touch(nb)
    db.commit()
    return user_msg, assistant_msg
