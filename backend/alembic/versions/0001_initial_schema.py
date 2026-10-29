"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Dimensión fijada en esta migración; debe coincidir con EMBEDDING_DIMENSIONS.
EMBEDDING_DIMENSIONS = 768


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"
    json_type = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

    if is_pg:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        from pgvector.sqlalchemy import Vector

        embedding_type = Vector(EMBEDDING_DIMENSIONS)
    else:
        embedding_type = sa.JSON()

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        *_ts(),
    )
    op.create_table(
        "notebooks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500)),
        *_ts(),
    )
    op.create_index("ix_notebooks_owner_id", "notebooks", ["owner_id"])

    op.create_table(
        "sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notebook_id", sa.Uuid(), sa.ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(120)),
        sa.Column("size_bytes", sa.BigInteger()),
        sa.Column("storage_key", sa.String(500)),
        sa.Column("url", sa.String(2048)),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_message", sa.Text()),
        *_ts(),
        sa.UniqueConstraint("notebook_id", "content_hash", name="uq_sources_notebook_hash"),
    )
    op.create_index("ix_sources_notebook_id", "sources", ["notebook_id"])

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", embedding_type, nullable=True),
        *_ts(),
        sa.UniqueConstraint("source_id", "position", name="uq_chunks_source_position"),
    )
    op.create_index("ix_document_chunks_source_id", "document_chunks", ["source_id"])

    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notebook_id", sa.Uuid(), sa.ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200)),
        *_ts(),
    )
    op.create_index("ix_conversations_notebook_id", "conversations", ["notebook_id"])

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "conversation_id", sa.Uuid(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", json_type),
        *_ts(),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "generated_artifacts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("notebook_id", sa.Uuid(), sa.ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(32), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("content", json_type),
        sa.Column("error_message", sa.Text()),
        *_ts(),
    )
    op.create_index("ix_generated_artifacts_notebook_id", "generated_artifacts", ["notebook_id"])

    op.create_table(
        "artifact_sources",
        sa.Column(
            "artifact_id", sa.Uuid(), sa.ForeignKey("generated_artifacts.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    for table in (
        "artifact_sources",
        "generated_artifacts",
        "messages",
        "conversations",
        "document_chunks",
        "sources",
        "notebooks",
        "users",
    ):
        op.drop_table(table)
