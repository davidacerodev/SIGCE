import uuid
from typing import Any

from sqlalchemy import (
    BigInteger,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampedIdMixin
from app.models.enums import (
    ArtifactStatus,
    ArtifactType,
    MessageRole,
    SourceStatus,
    SourceType,
)
from app.models.types import EmbeddingType, JsonType


def _enum(e: type) -> Enum:
    # Almacenado como texto (sin tipo ENUM nativo) para simplificar migraciones.
    return Enum(e, native_enum=False, length=32, values_callable=lambda x: [m.value for m in x])


artifact_sources = Table(
    "artifact_sources",
    Base.metadata,
    Column("artifact_id", Uuid, ForeignKey("generated_artifacts.id", ondelete="CASCADE"), primary_key=True),
    Column("source_id", Uuid, ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
)


class User(TimestampedIdMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    notebooks: Mapped[list["Notebook"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Notebook(TimestampedIdMixin, Base):
    __tablename__ = "notebooks"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    owner: Mapped[User] = relationship(back_populates="notebooks")
    sources: Mapped[list["Source"]] = relationship(back_populates="notebook", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="notebook", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["GeneratedArtifact"]] = relationship(
        back_populates="notebook", cascade="all, delete-orphan"
    )


class Source(TimestampedIdMixin, Base):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("notebook_id", "content_hash", name="uq_sources_notebook_hash"),)

    notebook_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notebooks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[SourceType] = mapped_column(_enum(SourceType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    storage_key: Mapped[str | None] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(2048))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[SourceStatus] = mapped_column(
        _enum(SourceStatus), default=SourceStatus.PENDING, nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    notebook: Mapped[Notebook] = relationship(back_populates="sources")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="source", cascade="all, delete-orphan")


class DocumentChunk(TimestampedIdMixin, Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("source_id", "position", name="uq_chunks_source_position"),)

    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), index=True, nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Nulo hasta que exista un proveedor real de embeddings.
    embedding: Mapped[Any | None] = mapped_column(EmbeddingType, nullable=True)

    source: Mapped[Source] = relationship(back_populates="chunks")


class Conversation(TimestampedIdMixin, Base):
    __tablename__ = "conversations"

    notebook_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notebooks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(200))

    notebook: Mapped[Notebook] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(TimestampedIdMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[MessageRole] = mapped_column(_enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[list[dict] | None] = mapped_column(JsonType)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class GeneratedArtifact(TimestampedIdMixin, Base):
    __tablename__ = "generated_artifacts"

    notebook_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notebooks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[ArtifactType] = mapped_column(_enum(ArtifactType), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[ArtifactStatus] = mapped_column(
        _enum(ArtifactStatus), default=ArtifactStatus.GENERATING, nullable=False
    )
    content: Mapped[dict | None] = mapped_column(JsonType)
    error_message: Mapped[str | None] = mapped_column(Text)

    notebook: Mapped[Notebook] = relationship(back_populates="artifacts")
    sources: Mapped[list[Source]] = relationship(secondary=artifact_sources)
