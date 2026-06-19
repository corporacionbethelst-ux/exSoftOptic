"""purchase receiving workflow

Revision ID: 20260618_0003
Revises: 20260618_0002
Create Date: 2026-06-18 00:03:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0003"
down_revision: Union[str, None] = "20260618_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("proveedores", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("nombre", sa.String(200), nullable=False), sa.Column("rfc", sa.String(20), nullable=True), sa.Column("email", sa.String(150), nullable=True), sa.Column("telefono", sa.String(30), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "rfc", name="uq_proveedores_empresa_rfc"))
    op.create_index(op.f("ix_proveedores_empresa_id"), "proveedores", ["empresa_id"])
    op.create_table("ordenes_compra", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("proveedor_id", sa.UUID(), nullable=False), sa.Column("folio", sa.String(40), nullable=False), sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("subtotal", sa.Numeric(15, 4), nullable=False), sa.Column("impuestos", sa.Numeric(15, 4), nullable=False), sa.Column("total", sa.Numeric(15, 4), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["proveedor_id"], ["proveedores.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_oc_empresa_folio"))
    op.create_index(op.f("ix_ordenes_compra_empresa_id"), "ordenes_compra", ["empresa_id"])
    op.create_index(op.f("ix_ordenes_compra_sucursal_id"), "ordenes_compra", ["sucursal_id"])
    op.create_index(op.f("ix_ordenes_compra_proveedor_id"), "ordenes_compra", ["proveedor_id"])
    op.create_table("ordenes_compra_lineas", sa.Column("orden_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("descripcion", sa.String(300), nullable=False), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("cantidad_recibida", sa.Numeric(15, 3), nullable=False), sa.Column("costo_unitario", sa.Numeric(15, 4), nullable=False), sa.Column("importe", sa.Numeric(15, 4), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["orden_id"], ["ordenes_compra.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_ordenes_compra_lineas_orden_id"), "ordenes_compra_lineas", ["orden_id"])
    op.create_index(op.f("ix_ordenes_compra_lineas_producto_id"), "ordenes_compra_lineas", ["producto_id"])
    op.create_table("recepciones_compra", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("orden_id", sa.UUID(), nullable=False), sa.Column("asiento_id", sa.UUID(), nullable=True), sa.Column("folio", sa.String(40), nullable=False), sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("total", sa.Numeric(15, 4), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["orden_id"], ["ordenes_compra.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_recepcion_empresa_folio"))
    op.create_index(op.f("ix_recepciones_compra_empresa_id"), "recepciones_compra", ["empresa_id"])
    op.create_index(op.f("ix_recepciones_compra_sucursal_id"), "recepciones_compra", ["sucursal_id"])
    op.create_index(op.f("ix_recepciones_compra_orden_id"), "recepciones_compra", ["orden_id"])
    op.create_table("recepciones_compra_lineas", sa.Column("recepcion_id", sa.UUID(), nullable=False), sa.Column("orden_linea_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("costo_unitario", sa.Numeric(15, 4), nullable=False), sa.Column("importe", sa.Numeric(15, 4), nullable=False), sa.Column("lote", sa.String(80), nullable=True), sa.Column("numero_serie", sa.String(120), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["orden_linea_id"], ["ordenes_compra_lineas.id"]), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.ForeignKeyConstraint(["recepcion_id"], ["recepciones_compra.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_recepciones_compra_lineas_recepcion_id"), "recepciones_compra_lineas", ["recepcion_id"])
    op.create_index(op.f("ix_recepciones_compra_lineas_orden_linea_id"), "recepciones_compra_lineas", ["orden_linea_id"])
    op.create_index(op.f("ix_recepciones_compra_lineas_producto_id"), "recepciones_compra_lineas", ["producto_id"])


def downgrade() -> None:
    op.drop_table("recepciones_compra_lineas")
    op.drop_table("recepciones_compra")
    op.drop_table("ordenes_compra_lineas")
    op.drop_table("ordenes_compra")
    op.drop_table("proveedores")
