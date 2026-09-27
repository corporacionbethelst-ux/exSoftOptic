from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class CuentaBancaria(BaseModel):
    __tablename__ = "cuentas_bancarias"
    __table_args__ = (UniqueConstraint("empresa_id", "numero_cuenta", name="uq_cuentas_bancarias_empresa_numero"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    cuenta_contable_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_contables.id"), nullable=False, index=True)
    banco = Column(String(120), nullable=False)
    numero_cuenta = Column(String(80), nullable=False)
    moneda = Column(String(3), nullable=False, default="MXN")
    estado = Column(String(30), nullable=False, default="ACTIVA")

    cuenta_contable = relationship("CuentaContable")
    movimientos = relationship("MovimientoBancario", back_populates="cuenta_bancaria")


class MovimientoBancario(BaseModel):
    __tablename__ = "movimientos_bancarios"
    __table_args__ = (UniqueConstraint("cuenta_bancaria_id", "referencia", "fecha", "monto", name="uq_mov_bancario_cuenta_ref_fecha_monto"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    cuenta_bancaria_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_bancarias.id"), nullable=False, index=True)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    referencia = Column(String(120), nullable=False)
    descripcion = Column(String(300), nullable=True)
    monto = Column(Numeric(15, 4), nullable=False)
    tipo = Column(String(20), nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    conciliado_en = Column(DateTime(timezone=True), nullable=True)

    cuenta_bancaria = relationship("CuentaBancaria", back_populates="movimientos")
    asiento = relationship("AsientoContable")


class ConciliacionBancaria(BaseModel):
    __tablename__ = "conciliaciones_bancarias"

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    cuenta_bancaria_id = Column(UUID(as_uuid=True), ForeignKey("cuentas_bancarias.id"), nullable=False, index=True)
    movimiento_id = Column(UUID(as_uuid=True), ForeignKey("movimientos_bancarios.id"), nullable=False, index=True)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estado = Column(String(30), nullable=False, default="CONCILIADA")
    observaciones = Column(Text, nullable=True)

    cuenta_bancaria = relationship("CuentaBancaria")
    movimiento = relationship("MovimientoBancario")
    asiento = relationship("AsientoContable")
