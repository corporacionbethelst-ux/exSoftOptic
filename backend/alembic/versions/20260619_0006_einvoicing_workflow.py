"""einvoicing workflow

Revision ID: 20260619_0006
Revises: 20260619_0005
Create Date: 2026-06-19 00:06:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0006"
down_revision: Union[str, None] = "20260619_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("facturas", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("venta_id", sa.UUID(), nullable=False), sa.Column("cliente_id", sa.UUID(), nullable=False), sa.Column("folio", sa.String(40), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("moneda", sa.String(3), nullable=False), sa.Column("subtotal", sa.Numeric(15, 4), nullable=False), sa.Column("impuestos", sa.Numeric(15, 4), nullable=False), sa.Column("total", sa.Numeric(15, 4), nullable=False), sa.Column("proveedor", sa.String(60), nullable=False), sa.Column("uuid_fiscal", sa.String(80), nullable=True), sa.Column("xml_url", sa.String(500), nullable=True), sa.Column("pdf_url", sa.String(500), nullable=True), sa.Column("error", sa.Text(), nullable=True), sa.Column("fecha_timbrado", sa.DateTime(timezone=True), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_facturas_empresa_folio"))
    op.create_index(op.f("ix_facturas_empresa_id"), "facturas", ["empresa_id"])
    op.create_index(op.f("ix_facturas_sucursal_id"), "facturas", ["sucursal_id"])
    op.create_index(op.f("ix_facturas_venta_id"), "facturas", ["venta_id"])
    op.create_index(op.f("ix_facturas_cliente_id"), "facturas", ["cliente_id"])
    op.create_index(op.f("ix_facturas_uuid_fiscal"), "facturas", ["uuid_fiscal"])
    op.create_table("facturas_lineas", sa.Column("factura_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("descripcion", sa.String(300), nullable=False), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("precio_unitario", sa.Numeric(15, 4), nullable=False), sa.Column("descuento", sa.Numeric(15, 4), nullable=False), sa.Column("importe", sa.Numeric(15, 4), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["factura_id"], ["facturas.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_facturas_lineas_factura_id"), "facturas_lineas", ["factura_id"])
    op.create_index(op.f("ix_facturas_lineas_producto_id"), "facturas_lineas", ["producto_id"])
    op.create_table("facturas_eventos", sa.Column("factura_id", sa.UUID(), nullable=False), sa.Column("tipo_evento", sa.String(40), nullable=False), sa.Column("descripcion", sa.Text(), nullable=False), sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["factura_id"], ["facturas.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_facturas_eventos_factura_id"), "facturas_eventos", ["factura_id"])


def downgrade() -> None:
    op.drop_table("facturas_eventos")
    op.drop_table("facturas_lineas")
    op.drop_table("facturas")
