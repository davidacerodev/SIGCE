import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ArtifactStatus, ArtifactType, MessageRole, SourceStatus, SourceType


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Credentials(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=320)
    password: str = Field(min_length=8, max_length=128)


class RegisterIn(Credentials):
    display_name: str = Field(min_length=1, max_length=120)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORM):
    id: uuid.UUID
    email: str
    display_name: str


class NotebookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)


class NotebookPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)


class NotebookOut(ORM):
    id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    source_count: int = 0


class TextSourceIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=2_000_000)


class SourceOut(ORM):
    id: uuid.UUID
    notebook_id: uuid.UUID
    type: SourceType
    name: str
    mime_type: str | None
    size_bytes: int | None
    status: SourceStatus
    error_message: str | None
    created_at: datetime


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    source_ids: list[uuid.UUID] | None = None


class MessageOut(ORM):
    id: uuid.UUID
    role: MessageRole
    content: str
    citations: list[dict] | None
    created_at: datetime


class ChatOut(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut


class ArtifactIn(BaseModel):
    type: ArtifactType
    source_ids: list[uuid.UUID] | None = None


class ArtifactOut(ORM):
    id: uuid.UUID
    type: ArtifactType
    title: str
    status: ArtifactStatus
    content: dict | None
    error_message: str | None
    created_at: datetime
