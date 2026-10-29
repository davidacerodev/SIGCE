from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB

from app.core.config import get_settings

# JSONB en PostgreSQL, JSON en otros motores (p. ej. SQLite en pruebas).
JsonType = JSON().with_variant(JSONB(), "postgresql")


class EmbeddingType(TypeDecorator):
    """Vector de pgvector en PostgreSQL; JSON en otros motores (solo pruebas)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(get_settings().embedding_dimensions))
        return dialect.type_descriptor(JSON())
