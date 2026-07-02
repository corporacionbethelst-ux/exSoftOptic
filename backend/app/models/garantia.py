from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Garantia(BaseModel):
    __tablename__ = "garantias"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_garantias_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id"), nullable=False, index=True)
    orden_laboratorio_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id"), nullable=True, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True, index=True)
    folio = Column(String(40), nullable=False)
    tipo = Column(String(30), nullable=False)
    estado = Column(String(30), nullable=False, default="ACTIVA")
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    descripcion = Column(Text, nullable=True)
    condiciones = Column(Text, nullable=True)

    reclamaciones = relationship("ReclamacionGarantia", back_populates="garantia", cascade="all, delete-orphan")
    eventos = relationship("EventoGarantia", back_populates="garantia", cascade="all, delete-orphan")


class ReclamacionGarantia(BaseModel):
    __tablename__ = "garantias_reclamaciones"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_reclamaciones_garantia_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    garantia_id = Column(UUID(as_uuid=True), ForeignKey("garantias.id", ondelete="CASCADE"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    motivo = Column(String(300), nullable=False)
    estado = Column(String(30), nullable=False, default="ABIERTA")
    resolucion = Column(Text, nullable=True)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)

    garantia = relationship("Garantia", back_populates="reclamaciones")


class EventoGarantia(BaseModel):
    __tablename__ = "garantias_eventos"

    garantia_id = Column(UUID(as_uuid=True), ForeignKey("garantias.id", ondelete="CASCADE"), nullable=False, index=True)
    reclamacion_id = Column(UUID(as_uuid=True), ForeignKey("garantias_reclamaciones.id"), nullable=True, index=True)
    tipo_evento = Column(String(40), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    garantia = relationship("Garantia", back_populates="eventos")
