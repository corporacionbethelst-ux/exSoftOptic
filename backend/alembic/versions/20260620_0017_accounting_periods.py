"""accounting periods

Revision ID: 20260620_0017
Revises: 20260619_0016
Create Date: 2026-06-20 00:17:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260620_0017"
down_revision: Union[str, None] = "20260619_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "periodos_contables",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "codigo", name="uq_periodos_empresa_codigo"),
    )
    op.create_index(op.f("ix_periodos_contables_empresa_id"), "periodos_contables", ["empresa_id"])
    op.create_index(op.f("ix_periodos_contables_fecha_inicio"), "periodos_contables", ["fecha_inicio"])
    op.create_index(op.f("ix_periodos_contables_fecha_fin"), "periodos_contables", ["fecha_fin"])
    op.create_index(op.f("ix_periodos_contables_estado"), "periodos_contables", ["estado"])
    op.create_index("ix_periodos_contables_empresa_fechas", "periodos_contables", ["empresa_id", "fecha_inicio", "fecha_fin"])


def downgrade() -> None:
    op.drop_index("ix_periodos_contables_empresa_fechas", table_name="periodos_contables")
    op.drop_table("periodos_contables")
