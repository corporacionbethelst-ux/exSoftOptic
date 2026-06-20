"""optical crm workflow

Revision ID: 20260619_0011
Revises: 20260619_0010
Create Date: 2026-06-19 00:11:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0011"
down_revision: Union[str, None] = "20260619_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "citas_opticas",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("sucursal_id", sa.UUID(), nullable=False),
        sa.Column("cliente_id", sa.UUID(), nullable=False),
        sa.Column("paciente_id", sa.UUID(), nullable=True),
        sa.Column("optometrista_id", sa.UUID(), nullable=True),
        sa.Column("folio", sa.String(40), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("motivo", sa.String(250), nullable=True),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["optometrista_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]),
        sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "folio", name="uq_citas_opticas_empresa_folio"),
    )
    op.create_index(op.f("ix_citas_opticas_empresa_id"), "citas_opticas", ["empresa_id"])
    op.create_index(op.f("ix_citas_opticas_sucursal_id"), "citas_opticas", ["sucursal_id"])
    op.create_index(op.f("ix_citas_opticas_cliente_id"), "citas_opticas", ["cliente_id"])
    op.create_index(op.f("ix_citas_opticas_paciente_id"), "citas_opticas", ["paciente_id"])
    op.create_index(op.f("ix_citas_opticas_optometrista_id"), "citas_opticas", ["optometrista_id"])
    op.create_index(op.f("ix_citas_opticas_fecha_inicio"), "citas_opticas", ["fecha_inicio"])
    op.create_table(
        "recordatorios_clientes",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("cliente_id", sa.UUID(), nullable=False),
        sa.Column("paciente_id", sa.UUID(), nullable=True),
        sa.Column("cita_id", sa.UUID(), nullable=True),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("canal", sa.String(30), nullable=False),
        sa.Column("programado_para", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cita_id"], ["citas_opticas.id"]),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["paciente_id"], ["pacientes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recordatorios_clientes_empresa_id"), "recordatorios_clientes", ["empresa_id"])
    op.create_index(op.f("ix_recordatorios_clientes_cliente_id"), "recordatorios_clientes", ["cliente_id"])
    op.create_index(op.f("ix_recordatorios_clientes_paciente_id"), "recordatorios_clientes", ["paciente_id"])
    op.create_index(op.f("ix_recordatorios_clientes_cita_id"), "recordatorios_clientes", ["cita_id"])
    op.create_index(op.f("ix_recordatorios_clientes_programado_para"), "recordatorios_clientes", ["programado_para"])


def downgrade() -> None:
    op.drop_table("recordatorios_clientes")
    op.drop_table("citas_opticas")
