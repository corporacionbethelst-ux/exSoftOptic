from sqlalchemy import Boolean, CheckConstraint, Column, Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CuentaContable(BaseModel):
    __tablename__ = "cuentas_contables"
    __table_args__ = (UniqueConstraint("empresa_id", "codigo", name="uq_cuentas_empresa_codigo"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    codigo = Column(String(40), nullable=False)
    nombre = Column(String(200), nullable=False)
    tipo = Column(String(30), nullable=False)
    naturaleza = Column(String(10), nullable=False)
    padre_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=True)
    acepta_movimientos = Column(Boolean, default=True, nullable=False)

    padre = relationship("CuentaContable", remote_side="CuentaContable.id")


class PeriodoContable(BaseModel):
    __tablename__ = "periodos_contables"
    __table_args__ = (UniqueConstraint("empresa_id", "codigo", name="uq_periodos_empresa_codigo"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    codigo = Column(String(20), nullable=False)
    nombre = Column(String(120), nullable=False)
    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=False, index=True)
    estado = Column(String(20), nullable=False, default="ABIERTO", index=True)


class AsientoContable(BaseModel):
    __tablename__ = "asientos_contables"
    __table_args__ = (Index("ix_asientos_empresa_fecha", "empresa_id", "fecha"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(500), nullable=False)
    origen = Column(String(80), nullable=False)
    referencia = Column(String(120), nullable=True)
    moneda = Column(String(3), nullable=False, default="MXN")
    estado = Column(String(20), nullable=False, default="CONTABILIZADO")

    lineas = relationship("LineaAsientoContable", back_populates="asiento", cascade="all, delete-orphan")


class LineaAsientoContable(BaseModel):
    __tablename__ = "lineas_asiento_contable"
    __table_args__ = (
        CheckConstraint("debe >= 0", name="ck_linea_debe_no_negativo"),
        CheckConstraint("haber >= 0", name="ck_linea_haber_no_negativo"),
    )

    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=False, index=True)
    descripcion = Column(String(300), nullable=True)
    debe = Column(Numeric(15, 4), nullable=False, default=0)
    haber = Column(Numeric(15, 4), nullable=False, default=0)
    centro_costo_id = Column(UUID(as_uuid=True), nullable=True)

    asiento = relationship("AsientoContable", back_populates="lineas")
    cuenta = relationship("CuentaContable")
