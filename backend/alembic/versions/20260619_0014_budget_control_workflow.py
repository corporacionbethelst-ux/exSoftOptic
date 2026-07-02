"""budget control workflow

Revision ID: 20260619_0014
Revises: 20260619_0013
Create Date: 2026-06-19 00:14:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0014"
down_revision: Union[str, None] = "20260619_0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "centros_costo",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("descripcion", sa.String(500), nullable=True),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "codigo", name="uq_centros_costo_empresa_codigo"),
    )
    op.create_index(op.f("ix_centros_costo_empresa_id"), "centros_costo", ["empresa_id"])
    op.create_table(
        "presupuestos",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("centro_costo_id", sa.UUID(), nullable=False),
        sa.Column("folio", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(180), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["centro_costo_id"], ["centros_costo.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "folio", name="uq_presupuestos_empresa_folio"),
    )
    op.create_index(op.f("ix_presupuestos_empresa_id"), "presupuestos", ["empresa_id"])
    op.create_index(op.f("ix_presupuestos_centro_costo_id"), "presupuestos", ["centro_costo_id"])
    op.create_table(
        "presupuestos_lineas",
        sa.Column("presupuesto_id", sa.UUID(), nullable=False),
        sa.Column("cuenta_codigo", sa.String(40), nullable=False),
        sa.Column("monto", sa.Numeric(15, 4), nullable=False),
        sa.Column("monto_comprometido", sa.Numeric(15, 4), nullable=False),
        sa.Column("monto_ejercido", sa.Numeric(15, 4), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["presupuesto_id"], ["presupuestos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_presupuestos_lineas_presupuesto_id"), "presupuestos_lineas", ["presupuesto_id"])
    op.create_index(op.f("ix_presupuestos_lineas_cuenta_codigo"), "presupuestos_lineas", ["cuenta_codigo"])


def downgrade() -> None:
    op.drop_table("presupuestos_lineas")
    op.drop_table("presupuestos")
    op.drop_table("centros_costo")
