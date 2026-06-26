"""optical lab workflow

Revision ID: 20260619_0004
Revises: 20260618_0003
Create Date: 2026-06-19 00:04:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0004"
down_revision: Union[str, None] = "20260618_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("ordenes_laboratorio", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("venta_id", sa.UUID(), nullable=False), sa.Column("paciente_id", sa.UUID(), nullable=False), sa.Column("receta_id", sa.UUID(), nullable=True), sa.Column("folio", sa.String(40), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("prioridad", sa.String(20), nullable=False), sa.Column("fecha_prometida", sa.DateTime(timezone=True), nullable=True), sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=True), sa.Column("fecha_terminada", sa.DateTime(timezone=True), nullable=True), sa.Column("fecha_entrega", sa.DateTime(timezone=True), nullable=True), sa.Column("observaciones", sa.Text(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]), sa.ForeignKeyConstraint(["receta_id"], ["recetas_opticas.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_lab_orden_empresa_folio"))
    op.create_index(op.f("ix_ordenes_laboratorio_empresa_id"), "ordenes_laboratorio", ["empresa_id"])
    op.create_index(op.f("ix_ordenes_laboratorio_sucursal_id"), "ordenes_laboratorio", ["sucursal_id"])
    op.create_index(op.f("ix_ordenes_laboratorio_venta_id"), "ordenes_laboratorio", ["venta_id"])
    op.create_index(op.f("ix_ordenes_laboratorio_paciente_id"), "ordenes_laboratorio", ["paciente_id"])
    op.create_table("ordenes_laboratorio_etapas", sa.Column("orden_id", sa.UUID(), nullable=False), sa.Column("etapa", sa.String(40), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("responsable_id", sa.UUID(), nullable=True), sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=True), sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=True), sa.Column("observaciones", sa.Text(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["orden_id"], ["ordenes_laboratorio.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["responsable_id"], ["usuarios.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("orden_id", "etapa", name="uq_lab_etapa_orden_etapa"))
    op.create_index(op.f("ix_ordenes_laboratorio_etapas_orden_id"), "ordenes_laboratorio_etapas", ["orden_id"])
    op.create_table("laboratorio_consumos_material", sa.Column("orden_id", sa.UUID(), nullable=False), sa.Column("producto_id", sa.UUID(), nullable=False), sa.Column("kardex_movimiento_id", sa.UUID(), nullable=True), sa.Column("cantidad", sa.Numeric(15, 3), nullable=False), sa.Column("costo_total", sa.Numeric(15, 4), nullable=False), sa.Column("observaciones", sa.Text(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["kardex_movimiento_id"], ["kardex_movimientos.id"]), sa.ForeignKeyConstraint(["orden_id"], ["ordenes_laboratorio.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["producto_id"], ["productos.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_laboratorio_consumos_material_orden_id"), "laboratorio_consumos_material", ["orden_id"])
    op.create_index(op.f("ix_laboratorio_consumos_material_producto_id"), "laboratorio_consumos_material", ["producto_id"])
    op.create_table("laboratorio_control_calidad", sa.Column("orden_id", sa.UUID(), nullable=False), sa.Column("resultado", sa.String(30), nullable=False), sa.Column("motivo_rechazo", sa.String(300), nullable=True), sa.Column("observaciones", sa.Text(), nullable=True), sa.Column("usuario_id", sa.UUID(), nullable=True), sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["orden_id"], ["ordenes_laboratorio.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_laboratorio_control_calidad_orden_id"), "laboratorio_control_calidad", ["orden_id"])


def downgrade() -> None:
    op.drop_table("laboratorio_control_calidad")
    op.drop_table("laboratorio_consumos_material")
    op.drop_table("ordenes_laboratorio_etapas")
    op.drop_table("ordenes_laboratorio")
