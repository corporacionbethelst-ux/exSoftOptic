"""optical warranty workflow

Revision ID: 20260619_0005
Revises: 20260619_0004
Create Date: 2026-06-19 00:05:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0005"
down_revision: Union[str, None] = "20260619_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("garantias", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=False), sa.Column("venta_id", sa.UUID(), nullable=False), sa.Column("orden_laboratorio_id", sa.UUID(), nullable=True), sa.Column("paciente_id", sa.UUID(), nullable=True), sa.Column("folio", sa.String(40), nullable=False), sa.Column("tipo", sa.String(30), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("fecha_inicio", sa.Date(), nullable=False), sa.Column("fecha_fin", sa.Date(), nullable=False), sa.Column("descripcion", sa.Text(), nullable=True), sa.Column("condiciones", sa.Text(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["orden_laboratorio_id"], ["ordenes_laboratorio.id"]), sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.ForeignKeyConstraint(["venta_id"], ["ventas.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_garantias_empresa_folio"))
    op.create_index(op.f("ix_garantias_empresa_id"), "garantias", ["empresa_id"])
    op.create_index(op.f("ix_garantias_sucursal_id"), "garantias", ["sucursal_id"])
    op.create_index(op.f("ix_garantias_venta_id"), "garantias", ["venta_id"])
    op.create_index(op.f("ix_garantias_orden_laboratorio_id"), "garantias", ["orden_laboratorio_id"])
    op.create_index(op.f("ix_garantias_paciente_id"), "garantias", ["paciente_id"])
    op.create_table("garantias_reclamaciones", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("garantia_id", sa.UUID(), nullable=False), sa.Column("folio", sa.String(40), nullable=False), sa.Column("motivo", sa.String(300), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("resolucion", sa.Text(), nullable=True), sa.Column("fecha_cierre", sa.DateTime(timezone=True), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["garantia_id"], ["garantias.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_reclamaciones_garantia_empresa_folio"))
    op.create_index(op.f("ix_garantias_reclamaciones_empresa_id"), "garantias_reclamaciones", ["empresa_id"])
    op.create_index(op.f("ix_garantias_reclamaciones_garantia_id"), "garantias_reclamaciones", ["garantia_id"])
    op.create_table("garantias_eventos", sa.Column("garantia_id", sa.UUID(), nullable=False), sa.Column("reclamacion_id", sa.UUID(), nullable=True), sa.Column("tipo_evento", sa.String(40), nullable=False), sa.Column("descripcion", sa.Text(), nullable=False), sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["garantia_id"], ["garantias.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["reclamacion_id"], ["garantias_reclamaciones.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_garantias_eventos_garantia_id"), "garantias_eventos", ["garantia_id"])
    op.create_index(op.f("ix_garantias_eventos_reclamacion_id"), "garantias_eventos", ["reclamacion_id"])


def downgrade() -> None:
    op.drop_table("garantias_eventos")
    op.drop_table("garantias_reclamaciones")
    op.drop_table("garantias")
