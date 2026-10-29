from app.integrations.ai.base import AnswerResult, RetrievedChunk

DEMO_NOTICE = "Demostración: no hay un modelo de IA conectado; esto son fragmentos de tus fuentes, no una respuesta generada."


class MockProvider:
    """Adaptador sin IA: devuelve fragmentos recuperados y lo declara explícitamente."""

    name = "mock"

    def answer(self, question: str, chunks: list[RetrievedChunk]) -> AnswerResult:
        if not chunks:
            return AnswerResult(f"{DEMO_NOTICE}\n\nNo encontré fragmentos relacionados con tu pregunta en las fuentes seleccionadas.", [])
        lines = [DEMO_NOTICE, ""]
        citations = []
        for i, c in enumerate(chunks, start=1):
            lines.append(f"[{i}] {c.content[:300].strip()}")
            citations.append({"index": i, "source_id": c.source_id, "source_name": c.source_name, "position": c.position})
        return AnswerResult("\n".join(lines), citations)

    def generate(self, artifact_type: str, chunks: list[RetrievedChunk]) -> dict:
        return {
            "demo": True,
            "notice": DEMO_NOTICE,
            "type": artifact_type,
            "excerpts": [
                {"source_name": c.source_name, "position": c.position, "text": c.content[:400].strip()} for c in chunks
            ],
        }
