from sqlalchemy import Boolean, Column, Date, ForeignKey, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class Impuesto(BaseModel):
    __tablename__ = "impuestos"
    __table_args__ = (UniqueConstraint("empresa_id", "codigo", name="uq_impuestos_empresa_codigo"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    codigo = Column(String(40), nullable=False)
    nombre = Column(String(120), nullable=False)
    tipo = Column(String(30), nullable=False)
    tasa = Column(Numeric(9, 6), nullable=False)
    cuenta_contable_codigo = Column(String(50), nullable=True)
    es_retencion = Column(Boolean, default=False, nullable=False)


class SerieFolio(BaseModel):
    __tablename__ = "series_folios"
    __table_args__ = (UniqueConstraint("empresa_id", "documento", "serie", name="uq_series_folios_empresa_documento_serie"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=True, index=True)
    documento = Column(String(40), nullable=False)
    serie = Column(String(20), nullable=False)
    folio_actual = Column(Numeric(18, 0), nullable=False, default=0)
    formato = Column(String(80), nullable=False, default="{serie}-{folio:06d}")


class TipoCambio(BaseModel):
    __tablename__ = "tipos_cambio"
    __table_args__ = (UniqueConstraint("empresa_id", "moneda_origen", "moneda_destino", "fecha", name="uq_tipos_cambio_empresa_monedas_fecha"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    moneda_origen = Column(String(3), nullable=False)
    moneda_destino = Column(String(3), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    tasa = Column(Numeric(18, 8), nullable=False)
    fuente = Column(String(80), nullable=True)


class ReglaContable(BaseModel):
    __tablename__ = "reglas_contables"
    __table_args__ = (UniqueConstraint("empresa_id", "evento", name="uq_reglas_contables_empresa_evento"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    evento = Column(String(80), nullable=False)
    descripcion = Column(String(250), nullable=False)
    cuentas = Column(JSON, nullable=False, default=dict)
    condiciones = Column(JSON, nullable=False, default=dict)
