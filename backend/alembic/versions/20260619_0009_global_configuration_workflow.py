"""global configuration workflow

Revision ID: 20260619_0009
Revises: 20260619_0008
Create Date: 2026-06-19 00:09:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260619_0009"
down_revision: Union[str, None] = "20260619_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "impuestos",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("tasa", sa.Numeric(9, 6), nullable=False),
        sa.Column("cuenta_contable_codigo", sa.String(50), nullable=True),
        sa.Column("es_retencion", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "codigo", name="uq_impuestos_empresa_codigo"),
    )
    op.create_index(op.f("ix_impuestos_empresa_id"), "impuestos", ["empresa_id"])
    op.create_table(
        "series_folios",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("sucursal_id", sa.UUID(), nullable=True),
        sa.Column("documento", sa.String(40), nullable=False),
        sa.Column("serie", sa.String(20), nullable=False),
        sa.Column("folio_actual", sa.Numeric(18, 0), nullable=False),
        sa.Column("formato", sa.String(80), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.ForeignKeyConstraint(["sucursal_id"], ["sucursales.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "documento", "serie", name="uq_series_folios_empresa_documento_serie"),
    )
    op.create_index(op.f("ix_series_folios_empresa_id"), "series_folios", ["empresa_id"])
    op.create_index(op.f("ix_series_folios_sucursal_id"), "series_folios", ["sucursal_id"])
    op.create_table(
        "tipos_cambio",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("moneda_origen", sa.String(3), nullable=False),
        sa.Column("moneda_destino", sa.String(3), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("tasa", sa.Numeric(18, 8), nullable=False),
        sa.Column("fuente", sa.String(80), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "moneda_origen", "moneda_destino", "fecha", name="uq_tipos_cambio_empresa_monedas_fecha"),
    )
    op.create_index(op.f("ix_tipos_cambio_empresa_id"), "tipos_cambio", ["empresa_id"])
    op.create_index(op.f("ix_tipos_cambio_fecha"), "tipos_cambio", ["fecha"])
    op.create_table(
        "reglas_contables",
        sa.Column("empresa_id", sa.UUID(), nullable=False),
        sa.Column("evento", sa.String(80), nullable=False),
        sa.Column("descripcion", sa.String(250), nullable=False),
        sa.Column("cuentas", sa.JSON(), nullable=False),
        sa.Column("condiciones", sa.JSON(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "evento", name="uq_reglas_contables_empresa_evento"),
    )
    op.create_index(op.f("ix_reglas_contables_empresa_id"), "reglas_contables", ["empresa_id"])


def downgrade() -> None:
    op.drop_table("reglas_contables")
    op.drop_table("tipos_cambio")
    op.drop_table("series_folios")
    op.drop_table("impuestos")
