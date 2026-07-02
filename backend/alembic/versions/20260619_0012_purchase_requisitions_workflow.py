"""purchase requisitions workflow

Revision ID: 20260619_0012
Revises: 20260619_0011
Create Date: 2026-06-19 00:12:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0012"
down_revision: Union[str, None] = "20260619_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "solicitudes_compra",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("sucursal_id", sa.UUID(), nullable=False),
        sa.Column("folio", sa.String(40), nullable=False),
        sa.Column("origen", sa.String(40), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("observaciones", sa.String(500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "folio", name="uq_solicitudes_compra_empresa_folio"),
    )
    op.create_index(op.f("ix_solicitudes_compra_empresa_id"), "solicitudes_compra", ["empresa_id"])
    op.create_index(op.f("ix_solicitudes_compra_sucursal_id"), "solicitudes_compra", ["sucursal_id"])
    op.create_table(
        "solicitudes_compra_lineas",
        sa.Column("solicitud_id", sa.UUID(), nullable=False),
        sa.Column("producto_id", sa.UUID(), nullable=False),
        sa.Column("cantidad_sugerida", sa.Numeric(15, 3), nullable=False),
        sa.Column("costo_estimado", sa.Numeric(15, 4), nullable=False),
        sa.Column("motivo", sa.String(250), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]),
        sa.ForeignKeyConstraint(["solicitud_id"], ["solicitudes_compra.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_solicitudes_compra_lineas_solicitud_id"), "solicitudes_compra_lineas", ["solicitud_id"])
    op.create_index(op.f("ix_solicitudes_compra_lineas_producto_id"), "solicitudes_compra_lineas", ["producto_id"])


def downgrade() -> None:
    op.drop_table("solicitudes_compra_lineas")
    op.drop_table("solicitudes_compra")
