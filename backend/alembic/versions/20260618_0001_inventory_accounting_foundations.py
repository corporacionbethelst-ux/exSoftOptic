"""inventory and accounting foundations

Revision ID: 20260618_0001
Revises: 95ec8fddf9ad
Create Date: 2026-06-18 00:01:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0001"
down_revision: Union[str, None] = "95ec8fddf9ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("productos_sku_key", "productos", type_="unique")
    op.drop_constraint("productos_codigo_barras_key", "productos", type_="unique")
    op.drop_constraint("marcas_nombre_key", "marcas", type_="unique")
    op.create_unique_constraint("uq_categorias_empresa_nombre", "categorias", ["empresa_id", "nombre"])
    op.create_unique_constraint("uq_marcas_empresa_nombre", "marcas", ["empresa_id", "nombre"])
    op.add_column("productos", sa.Column("atributos_opticos", sa.JSON(), nullable=False, server_default="{}"))
    op.add_column("productos", sa.Column("requiere_lote", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("productos", sa.Column("requiere_serie", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_unique_constraint("uq_productos_empresa_sku", "productos", ["empresa_id", "sku"])
    op.create_unique_constraint("uq_productos_empresa_codigo_barras", "productos", ["empresa_id", "codigo_barras"])

    op.create_table("cuentas_contables", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("codigo", sa.String(40), nullable=False), sa.Column("nombre", sa.String(200), nullable=False), sa.Column("tipo", sa.String(30), nullable=False), sa.Column("naturaleza", sa.String(10), nullable=False), sa.Column("padre_id", sa.UUID(), nullable=True), sa.Column("acepta_movimientos", sa.Boolean(), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["padre_id"], ["cuentas_contables.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "codigo", name="uq_cuentas_empresa_codigo"))
    op.create_index(op.f("ix_cuentas_contables_empresa_id"), "cuentas_contables", ["empresa_id"])
    op.create_table("asientos_contables", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("fecha", sa.Date(), nullable=False), sa.Column("descripcion", sa.String(500), nullable=False), sa.Column("origen", sa.String(80), nullable=False), sa.Column("referencia", sa.String(120), nullable=True), sa.Column("moneda", sa.String(3), nullable=False), sa.Column("estado", sa.String(20), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_asientos_empresa_fecha", "asientos_contables", ["empresa_id", "fecha"])
    op.create_table("lineas_asiento_contable", sa.Column("asiento_id", sa.UUID(), nullable=False), sa.Column("cuenta_id", sa.UUID(), nullable=False), sa.Column("descripcion", sa.String(300), nullable=True), sa.Column("debe", sa.Numeric(15, 4), nullable=False), sa.Column("haber", sa.Numeric(15, 4), nullable=False), sa.Column("centro_costo_id", sa.UUID(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.CheckConstraint("debe >= 0", name="ck_linea_debe_no_negativo"), sa.CheckConstraint("haber >= 0", name="ck_linea_haber_no_negativo"), sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["cuenta_id"], ["cuentas_contables.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_lineas_asiento_contable_asiento_id"), "lineas_asiento_contable", ["asiento_id"])
    op.create_index(op.f("ix_lineas_asiento_contable_cuenta_id"), "lineas_asiento_contable", ["cuenta_id"])
    op.create_table("inventario_existencias", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("costo_promedio", sa.Numeric(15, 4), nullable=False), sa.Column("valor_total", sa.Numeric(15, 4), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "sucursal_id", "producto_id", name="uq_existencia_empresa_sucursal_producto"))
    op.create_table("inventario_capas", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("lote", sa.String(80), nullable=True), sa.Column("numero_serie", sa.String(120), nullable=True), sa.Column("fecha_caducidad", sa.Date(), nullable=True), sa.Column("cantidad_inicial", sa.Numeric(15, 3), nullable=False), sa.Column("cantidad_disponible", sa.Numeric(15, 3), nullable=False), sa.Column("costo_unitario", sa.Numeric(15, 4), nullable=False), sa.Column("referencia", sa.String(120), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_capas_peps", "inventario_capas", ["empresa_id", "sucursal_id", "producto_id", "created_at"])
    op.create_table("kardex_movimientos", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("tipo_movimiento", sa.String(30), nullable=False), sa.Column("origen", sa.String(80), nullable=False), sa.Column("referencia", sa.String(120), nullable=True), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("costo_unitario", sa.Numeric(15, 4), nullable=False), sa.Column("costo_total", sa.Numeric(15, 4), nullable=False), sa.Column("saldo_cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("saldo_valor", sa.Numeric(15, 4), nullable=False), sa.Column("lote", sa.String(80), nullable=True), sa.Column("numero_serie", sa.String(120), nullable=True), sa.Column("asiento_id", sa.UUID(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_kardex_producto_fecha", "kardex_movimientos", ["empresa_id", "producto_id", "created_at"])

def downgrade() -> None:
    op.drop_table("kardex_movimientos")
    op.drop_table("inventario_capas")
    op.drop_table("inventario_existencias")
    op.drop_table("lineas_asiento_contable")
    op.drop_table("asientos_contables")
    op.drop_table("cuentas_contables")
    op.drop_constraint("uq_productos_empresa_codigo_barras", "productos", type_="unique")
    op.drop_constraint("uq_productos_empresa_sku", "productos", type_="unique")
    op.drop_constraint("uq_marcas_empresa_nombre", "marcas", type_="unique")
    op.drop_constraint("uq_categorias_empresa_nombre", "categorias", type_="unique")
    op.create_unique_constraint("productos_sku_key", "productos", ["sku"])
    op.create_unique_constraint("productos_codigo_barras_key", "productos", ["codigo_barras"])
    op.create_unique_constraint("marcas_nombre_key", "marcas", ["nombre"])
    op.drop_column("productos", "requiere_serie")
    op.drop_column("productos", "requiere_lote")
    op.drop_column("productos", "atributos_opticos")
