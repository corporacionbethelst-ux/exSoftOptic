from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CitaOptica(BaseModel):
    __tablename__ = "citas_opticas"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_citas_opticas_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True, index=True)
    optometrista_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)
    folio = Column(String(40), nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False, index=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    tipo = Column(String(40), nullable=False, default="EXAMEN_VISUAL")
    estado = Column(String(30), nullable=False, default="PROGRAMADA")
    motivo = Column(String(250), nullable=True)
    observaciones = Column(Text, nullable=True)

    cliente = relationship("Cliente")
    paciente = relationship("Paciente")
    optometrista = relationship("Usuario")


class RecordatorioCliente(BaseModel):
    __tablename__ = "recordatorios_clientes"

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True, index=True)
    cita_id = Column(UUID(as_uuid=True), ForeignKey("citas_opticas.id"), nullable=True, index=True)
    tipo = Column(String(40), nullable=False)
    canal = Column(String(30), nullable=False, default="EMAIL")
    programado_para = Column(DateTime(timezone=True), nullable=False, index=True)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    mensaje = Column(Text, nullable=False)

    cliente = relationship("Cliente")
    paciente = relationship("Paciente")
    cita = relationship("CitaOptica")
