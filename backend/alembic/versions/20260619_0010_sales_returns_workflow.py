"""sales returns workflow

Revision ID: 20260619_0010
Revises: 20260619_0009
Create Date: 2026-06-19 00:10:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0010"
down_revision: Union[str, None] = "20260619_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ventas_devoluciones",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("sucursal_id", sa.UUID(), nullable=False),
        sa.Column("venta_id", sa.UUID(), nullable=False),
        sa.Column("asiento_id", sa.UUID(), nullable=True),
        sa.Column("folio", sa.String(40), nullable=False),
        sa.Column("motivo", sa.String(250), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("subtotal", sa.Numeric(15, 4), nullable=False),
        sa.Column("impuestos", sa.Numeric(15, 4), nullable=False),
        sa.Column("total", sa.Numeric(15, 4), nullable=False),
        sa.Column("costo_total", sa.Numeric(15, 4), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]),
        sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "folio", name="uq_devoluciones_venta_empresa_folio"),
    )
    op.create_index(op.f("ix_ventas_devoluciones_empresa_id"), "ventas_devoluciones", ["empresa_id"])
    op.create_index(op.f("ix_ventas_devoluciones_sucursal_id"), "ventas_devoluciones", ["sucursal_id"])
    op.create_index(op.f("ix_ventas_devoluciones_venta_id"), "ventas_devoluciones", ["venta_id"])
    op.create_table(
        "ventas_devoluciones_lineas",
        sa.Column("devolucion_id", sa.UUID(), nullable=False),
        sa.Column("venta_linea_id", sa.UUID(), nullable=False),
        sa.Column("producto_id", sa.UUID(), nullable=False),
        sa.Column("cantidad", sa.Numeric(15, 3), nullable=False),
        sa.Column("importe", sa.Numeric(15, 4), nullable=False),
        sa.Column("costo_total", sa.Numeric(15, 4), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["devolucion_id"], ["ventas_devoluciones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]),
        sa.ForeignKeyConstraint(["venta_linea_id"], ["ventas_lineas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ventas_devoluciones_lineas_devolucion_id"), "ventas_devoluciones_lineas", ["devolucion_id"])
    op.create_index(op.f("ix_ventas_devoluciones_lineas_venta_linea_id"), "ventas_devoluciones_lineas", ["venta_linea_id"])
    op.create_index(op.f("ix_ventas_devoluciones_lineas_producto_id"), "ventas_devoluciones_lineas", ["producto_id"])


def downgrade() -> None:
    op.drop_table("ventas_devoluciones_lineas")
    op.drop_table("ventas_devoluciones")
