from sqlalchemy import Column, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Empleado(BaseModel):
    __tablename__ = "empleados"
    __table_args__ = (UniqueConstraint("empresa_id", "numero_empleado", name="uq_empleados_empresa_numero"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=True, index=True)
    numero_empleado = Column(String(40), nullable=False)
    nombre = Column(String(200), nullable=False)
    email = Column(String(150), nullable=True)
    rfc = Column(String(20), nullable=True)
    curp = Column(String(25), nullable=True)
    nss = Column(String(20), nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    salario_diario = Column(Numeric(15, 4), nullable=False)
    estado = Column(String(30), nullable=False, default="ACTIVO")

    recibos = relationship("NominaRecibo", back_populates="empleado")


class NominaPeriodo(BaseModel):
    __tablename__ = "nomina_periodos"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_nomina_periodos_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    total_percepciones = Column(Numeric(15, 4), nullable=False, default=0)
    total_deducciones = Column(Numeric(15, 4), nullable=False, default=0)
    total_neto = Column(Numeric(15, 4), nullable=False, default=0)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True)
    observaciones = Column(Text, nullable=True)

    recibos = relationship("NominaRecibo", back_populates="periodo", cascade="all, delete-orphan")


class NominaRecibo(BaseModel):
    __tablename__ = "nomina_recibos"
    __table_args__ = (UniqueConstraint("periodo_id", "empleado_id", name="uq_nomina_recibo_periodo_empleado"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    periodo_id = Column(UUID(as_uuid=True), ForeignKey("nomina_periodos.id", ondelete="CASCADE"), nullable=False, index=True)
    empleado_id = Column(UUID(as_uuid=True), ForeignKey("empleados.id"), nullable=False, index=True)
    dias_pagados = Column(Numeric(8, 2), nullable=False)
    percepciones = Column(Numeric(15, 4), nullable=False, default=0)
    deducciones = Column(Numeric(15, 4), nullable=False, default=0)
    neto = Column(Numeric(15, 4), nullable=False, default=0)
    estado = Column(String(30), nullable=False, default="CALCULADO")

    periodo = relationship("NominaPeriodo", back_populates="recibos")
    empleado = relationship("Empleado", back_populates="recibos")
