"""treasury reconciliation workflow

Revision ID: 20260619_0013
Revises: 20260619_0012
Create Date: 2026-06-19 00:13:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0013"
down_revision: Union[str, None] = "20260619_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cuentas_bancarias",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("cuenta_contable_id", sa.UUID(), nullable=False),
        sa.Column("banco", sa.String(120), nullable=False),
        sa.Column("numero_cuenta", sa.String(80), nullable=False),
        sa.Column("moneda", sa.String(3), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["cuenta_contable_id"], ["cuentas_contables.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "numero_cuenta", name="uq_cuentas_bancarias_empresa_numero"),
    )
    op.create_index(op.f("ix_cuentas_bancarias_empresa_id"), "cuentas_bancarias", ["empresa_id"])
    op.create_index(op.f("ix_cuentas_bancarias_cuenta_contable_id"), "cuentas_bancarias", ["cuenta_contable_id"])
    op.create_table(
        "movimientos_bancarios",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("cuenta_bancaria_id", sa.UUID(), nullable=False),
        sa.Column("asiento_id", sa.UUID(), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("referencia", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.String(300), nullable=True),
        sa.Column("monto", sa.Numeric(15, 4), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("conciliado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]),
        sa.ForeignKeyConstraint(["cuenta_bancaria_id"], ["cuentas_bancarias.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cuenta_bancaria_id", "referencia", "fecha", "monto", name="uq_mov_bancario_cuenta_ref_fecha_monto"),
    )
    op.create_index(op.f("ix_movimientos_bancarios_empresa_id"), "movimientos_bancarios", ["empresa_id"])
    op.create_index(op.f("ix_movimientos_bancarios_cuenta_bancaria_id"), "movimientos_bancarios", ["cuenta_bancaria_id"])
    op.create_index(op.f("ix_movimientos_bancarios_asiento_id"), "movimientos_bancarios", ["asiento_id"])
    op.create_index(op.f("ix_movimientos_bancarios_fecha"), "movimientos_bancarios", ["fecha"])
    op.create_table(
        "conciliaciones_bancarias",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("cuenta_bancaria_id", sa.UUID(), nullable=False),
        sa.Column("movimiento_id", sa.UUID(), nullable=False),
        sa.Column("asiento_id", sa.UUID(), nullable=False),
        sa.Column("fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("estado", sa.String(30), nullable=False),
        sa.Column("observaciones", sa.Text(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["asiento_id"], ["asientos_contables.id"]),
        sa.ForeignKeyConstraint(["cuenta_bancaria_id"], ["cuentas_bancarias.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["movimiento_id"], ["movimientos_bancarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conciliaciones_bancarias_empresa_id"), "conciliaciones_bancarias", ["empresa_id"])
    op.create_index(op.f("ix_conciliaciones_bancarias_cuenta_bancaria_id"), "conciliaciones_bancarias", ["cuenta_bancaria_id"])
    op.create_index(op.f("ix_conciliaciones_bancarias_movimiento_id"), "conciliaciones_bancarias", ["movimiento_id"])
    op.create_index(op.f("ix_conciliaciones_bancarias_asiento_id"), "conciliaciones_bancarias", ["asiento_id"])


def downgrade() -> None:
    op.drop_table("conciliaciones_bancarias")
    op.drop_table("movimientos_bancarios")
    op.drop_table("cuentas_bancarias")
