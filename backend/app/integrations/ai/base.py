from dataclasses import dataclass
from typing import Protocol


@dataclass
class RetrievedChunk:
    source_id: str
    source_name: str
    position: int
    content: str


@dataclass
class AnswerResult:
    text: str
    citations: list[dict]


class AIProvider(Protocol):
    name: str

    def answer(self, question: str, chunks: list[RetrievedChunk]) -> AnswerResult: ...

    def generate(self, artifact_type: str, chunks: list[RetrievedChunk]) -> dict: ...
