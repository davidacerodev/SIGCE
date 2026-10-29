import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Conversation, DocumentChunk, Message, Notebook, Source, User
from app.models.enums import MessageRole, SourceStatus, SourceType


def _user(db):
    u = User(email="a@b.co", display_name="A", password_hash="x")
    db.add(u)
    db.commit()
    return u


def test_cascade_delete_notebook(db):
    u = _user(db)
    nb = Notebook(owner_id=u.id, title="Nb")
    src = Source(type=SourceType.TEXT, name="n.txt", content_hash="h1", notebook=nb)
    src.chunks.append(DocumentChunk(position=0, content="hola"))
    conv = Conversation(notebook=nb)
    conv.messages.append(Message(role=MessageRole.USER, content="hi", citations=[{"source": 1}]))
    db.add_all([nb, src, conv])
    db.commit()
    assert src.status == SourceStatus.PENDING

    db.delete(nb)
    db.commit()
    for model in (Source, DocumentChunk, Conversation, Message):
        assert db.query(model).count() == 0


def test_duplicate_source_hash_rejected_per_notebook(db):
    u = _user(db)
    nb = Notebook(owner_id=u.id, title="Nb")
    db.add(nb)
    db.commit()
    db.add(Source(notebook_id=nb.id, type=SourceType.FILE, name="a.pdf", content_hash="same"))
    db.commit()
    db.add(Source(notebook_id=nb.id, type=SourceType.FILE, name="b.pdf", content_hash="same"))
    with pytest.raises(IntegrityError):
        db.commit()
