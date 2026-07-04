"""audit log workflow

Revision ID: 20260619_0008
Revises: 20260619_0007
Create Date: 2026-06-19 00:08:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0008"
down_revision: Union[str, None] = "20260619_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auditoria_eventos",
        sa.Column("empresa_id", sa.UUID(), nullable=True),
        sa.Column("usuario_id", sa.UUID(), nullable=True),
        sa.Column("secuencia", sa.Integer(), nullable=False),
        sa.Column("accion", sa.String(80), nullable=False),
        sa.Column("entidad", sa.String(120), nullable=False),
        sa.Column("entidad_id", sa.String(80), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("previous_hash", sa.String(64), nullable=True),
        sa.Column("event_hash", sa.String(64), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_hash"),
    )
    op.create_index(op.f("ix_auditoria_eventos_empresa_id"), "auditoria_eventos", ["empresa_id"])
    op.create_index(op.f("ix_auditoria_eventos_usuario_id"), "auditoria_eventos", ["usuario_id"])
    op.create_index(op.f("ix_auditoria_eventos_secuencia"), "auditoria_eventos", ["secuencia"])
    op.create_index(op.f("ix_auditoria_eventos_accion"), "auditoria_eventos", ["accion"])
    op.create_index(op.f("ix_auditoria_eventos_entidad"), "auditoria_eventos", ["entidad"])
    op.create_index(op.f("ix_auditoria_eventos_entidad_id"), "auditoria_eventos", ["entidad_id"])
    op.create_index(op.f("ix_auditoria_eventos_event_hash"), "auditoria_eventos", ["event_hash"])
    op.create_index("ix_auditoria_eventos_empresa_secuencia", "auditoria_eventos", ["empresa_id", "secuencia"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_auditoria_eventos_empresa_secuencia", table_name="auditoria_eventos")
    op.drop_table("auditoria_eventos")
