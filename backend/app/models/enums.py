import enum


class SourceType(str, enum.Enum):
    FILE = "file"
    TEXT = "text"
    URL = "url"


class SourceStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class ArtifactType(str, enum.Enum):
    SUMMARY = "summary"
    FAQ = "faq"
    STUDY_GUIDE = "study_guide"
    FLASHCARDS = "flashcards"
    QUIZ = "quiz"
    MIND_MAP = "mind_map"


class ArtifactStatus(str, enum.Enum):
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"
