"""http idempotency keys

Revision ID: 20260619_0016
Revises: 20260619_0015
Create Date: 2026-06-19 00:16:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0016"
down_revision: Union[str, None] = "20260619_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("scope", sa.String(120), nullable=False),
        sa.Column("key", sa.String(180), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.JSON(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "scope", "key", name="uq_idempotency_empresa_scope_key"),
    )
    op.create_index(op.f("ix_idempotency_keys_empresa_id"), "idempotency_keys", ["empresa_id"])
    op.create_index(op.f("ix_idempotency_keys_scope"), "idempotency_keys", ["scope"])
    op.create_index(op.f("ix_idempotency_keys_key"), "idempotency_keys", ["key"])
    op.create_index(op.f("ix_idempotency_keys_status"), "idempotency_keys", ["status"])
    op.create_index(op.f("ix_idempotency_keys_locked_until"), "idempotency_keys", ["locked_until"])
    op.create_index(op.f("ix_idempotency_keys_expires_at"), "idempotency_keys", ["expires_at"])
    op.create_index("ix_idempotency_keys_lookup", "idempotency_keys", ["empresa_id", "scope", "key"])


def downgrade() -> None:
    op.drop_index("ix_idempotency_keys_lookup", table_name="idempotency_keys")
    op.drop_table("idempotency_keys")
