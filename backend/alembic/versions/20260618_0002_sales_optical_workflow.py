"""sales optical workflow

Revision ID: 20260618_0002
Revises: 20260618_0001
Create Date: 2026-06-18 00:02:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0002"
down_revision: Union[str, None] = "20260618_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("email", sa.String(150), nullable=True),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("rfc", sa.String(20), nullable=True),
        sa.Column("codigo_postal", sa.String(10), nullable=True),
        sa.Column("regimen_fiscal", sa.String(50), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "email", name="uq_clientes_empresa_email"),
    )
    op.create_index(op.f("ix_clientes_empresa_id"), "clientes", ["empresa_id"])
    op.create_index(op.f("ix_clientes_email"), "clientes", ["email"])

    op.create_table(
        "pacientes",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("cliente_id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("fecha_nacimiento", sa.Date(), nullable=True),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("email", sa.String(150), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pacientes_cliente_id"), "pacientes", ["cliente_id"])
    op.create_index(op.f("ix_pacientes_empresa_id"), "pacientes", ["empresa_id"])

    op.create_table(
        "recetas_opticas",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("paciente_id", sa.UUID(), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("od_esfera", sa.Numeric(5, 2), nullable=True),
        sa.Column("od_cilindro", sa.Numeric(5, 2), nullable=True),
        sa.Column("od_eje", sa.Numeric(5, 2), nullable=True),
        sa.Column("od_adicion", sa.Numeric(5, 2), nullable=True),
        sa.Column("oi_esfera", sa.Numeric(5, 2), nullable=True),
        sa.Column("oi_cilindro", sa.Numeric(5, 2), nullable=True),
        sa.Column("oi_eje", sa.Numeric(5, 2), nullable=True),
        sa.Column("oi_adicion", sa.Numeric(5, 2), nullable=True),
        sa.Column("dnp", sa.Numeric(5, 2), nullable=True),
        sa.Column("altura", sa.Numeric(5, 2), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recetas_opticas_empresa_id"), "recetas_opticas", ["empresa_id"])
    op.create_index(op.f("ix_recetas_opticas_paciente_id"), "recetas_opticas", ["paciente_id"])

    op.create_table(
        "ventas",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("sucursal_id", sa.UUID(), nullable=False),
        sa.Column("cliente_id", sa.UUID(), nullable=False),
        sa.Column("paciente_id", sa.UUID(), nullable=True),
        sa.Column("receta_id", sa.UUID(), nullable=True),
        sa.Column("asiento_id", sa.UUID(), nullable=True),
        sa.Column("folio", sa.String(40), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
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
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]),
        sa.ForeignKeyConstraint(["receta_id"], ["recetas_opticas.id"]),
        sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "folio", name="uq_ventas_empresa_folio"),
    )
    op.create_index(op.f("ix_ventas_cliente_id"), "ventas", ["cliente_id"])
    op.create_index(op.f("ix_ventas_empresa_id"), "ventas", ["empresa_id"])
    op.create_index(op.f("ix_ventas_paciente_id"), "ventas", ["paciente_id"])
    op.create_index(op.f("ix_ventas_sucursal_id"), "ventas", ["sucursal_id"])

    op.create_table(
        "ventas_lineas",
        sa.Column("venta_id", sa.UUID(), nullable=False),
        sa.Column("producto_id", sa.UUID(), nullable=False),
        sa.Column("descripcion", sa.String(300), nullable=False),
        sa.Column("cantidad", sa.Numeric(15, 3), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(15, 4), nullable=False),
        sa.Column("descuento", sa.Numeric(15, 4), nullable=False),
        sa.Column("importe", sa.Numeric(15, 4), nullable=False),
        sa.Column("costo_total", sa.Numeric(15, 4), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]),
        sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ventas_lineas_producto_id"), "ventas_lineas", ["producto_id"])
    op.create_index(op.f("ix_ventas_lineas_venta_id"), "ventas_lineas", ["venta_id"])

    op.create_table(
        "ventas_pagos",
        sa.Column("venta_id", sa.UUID(), nullable=False),
        sa.Column("metodo_pago", sa.String(40), nullable=False),
        sa.Column("monto", sa.Numeric(15, 4), nullable=False),
        sa.Column("referencia", sa.String(120), nullable=True),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ventas_pagos_venta_id"), "ventas_pagos", ["venta_id"])


def downgrade() -> None:
    op.drop_table("ventas_pagos")
    op.drop_table("ventas_lineas")
    op.drop_table("ventas")
    op.drop_table("recetas_opticas")
    op.drop_table("pacientes")
    op.drop_table("clientes")
