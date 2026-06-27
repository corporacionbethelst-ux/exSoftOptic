"""payroll workflow

Revision ID: 20260619_0007
Revises: 20260619_0006
Create Date: 2026-06-19 00:07:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0007"
down_revision: Union[str, None] = "20260619_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("empleados", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("sucursal_id", sa.UUID(), nullable=True), sa.Column("numero_empleado", sa.String(40), nullable=False), sa.Column("nombre", sa.String(200), nullable=False), sa.Column("email", sa.String(150), nullable=True), sa.Column("rfc", sa.String(20), nullable=True), sa.Column("curp", sa.String(25), nullable=True), sa.Column("nss", sa.String(20), nullable=True), sa.Column("fecha_ingreso", sa.Date(), nullable=False), sa.Column("salario_diario", sa.Numeric(15, 4), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "numero_empleado", name="uq_empleados_empresa_numero"))
    op.create_index(op.f("ix_empleados_empresa_id"), "empleados", ["empresa_id"])
    op.create_index(op.f("ix_empleados_sucursal_id"), "empleados", ["sucursal_id"])
    op.create_table("nomina_periodos", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("folio", sa.String(40), nullable=False), sa.Column("fecha_inicio", sa.Date(), nullable=False), sa.Column("fecha_fin", sa.Date(), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("total_percepciones", sa.Numeric(15, 4), nullable=False), sa.Column("total_deducciones", sa.Numeric(15, 4), nullable=False), sa.Column("total_neto", sa.Numeric(15, 4), nullable=False), sa.Column("asiento_id", sa.UUID(), nullable=True), sa.Column("observaciones", sa.Text(), nullable=True), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "folio", name="uq_nomina_periodos_empresa_folio"))
    op.create_index(op.f("ix_nomina_periodos_empresa_id"), "nomina_periodos", ["empresa_id"])
    op.create_table("nomina_recibos", sa.Column("empresa_id", sa.UUID(), nullable=False), sa.Column("periodo_id", sa.UUID(), nullable=False), sa.Column("empleado_id", sa.UUID(), nullable=False), sa.Column("dias_pagados", sa.Numeric(8, 2), nullable=False), sa.Column("percepciones", sa.Numeric(15, 4), nullable=False), sa.Column("deducciones", sa.Numeric(15, 4), nullable=False), sa.Column("neto", sa.Numeric(15, 4), nullable=False), sa.Column("estado", sa.String(30), nullable=False), sa.Column("id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("is_active", sa.Boolean(), nullable=False), sa.ForeignKeyConstraint(["empleado_id"], ["empleados.id"]), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]), sa.ForeignKeyConstraint(["periodo_id"], ["nomina_periodos.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("periodo_id", "empleado_id", name="uq_nomina_recibo_periodo_empleado"))
    op.create_index(op.f("ix_nomina_recibos_empresa_id"), "nomina_recibos", ["empresa_id"])
    op.create_index(op.f("ix_nomina_recibos_periodo_id"), "nomina_recibos", ["periodo_id"])
    op.create_index(op.f("ix_nomina_recibos_empleado_id"), "nomina_recibos", ["empleado_id"])


def downgrade() -> None:
    op.drop_table("nomina_recibos")
    op.drop_table("nomina_periodos")
    op.drop_table("empleados")
