from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class OrdenLaboratorio(BaseModel):
    __tablename__ = "ordenes_laboratorio"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_lab_orden_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True)
    receta_id = Column(UUID(as_uuid=True), ForeignKey("recetas_opticas.id"), nullable=True)
    folio = Column(String(40), nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    prioridad = Column(String(20), nullable=False, default="NORMAL")
    fecha_prometida = Column(DateTime(timezone=True), nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_terminada = Column(DateTime(timezone=True), nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)
    observaciones = Column(Text, nullable=True)

    etapas = relationship("OrdenLaboratorioEtapa", back_populates="orden", cascade="all, delete-orphan")
    consumos = relationship("ConsumoMaterialLaboratorio", back_populates="orden", cascade="all, delete-orphan")
    controles_calidad = relationship("ControlCalidadLaboratorio", back_populates="orden", cascade="all, delete-orphan")


class OrdenLaboratorioEtapa(BaseModel):
    __tablename__ = "ordenes_laboratorio_etapas"
    __table_args__ = (UniqueConstraint("orden_id", "etapa", name="uq_lab_etapa_orden_etapa"),)

    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id", ondelete="CASCADE"), nullable=False, index=True)
    etapa = Column(String(40), nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    responsable_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    observaciones = Column(Text, nullable=True)

    orden = relationship("OrdenLaboratorio", back_populates="etapas")


class ConsumoMaterialLaboratorio(BaseModel):
    __tablename__ = "laboratorio_consumos_material"

    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    kardex_movimiento_id = Column(UUID(as_uuid=True), ForeignKey("kardex_movimientos.id"), nullable=True)
    cantidad = Column(Numeric(15, 3), nullable=False)
    costo_total = Column(Numeric(15, 4), nullable=False)
    observaciones = Column(Text, nullable=True)

    orden = relationship("OrdenLaboratorio", back_populates="consumos")
    producto = relationship("Producto")


class ControlCalidadLaboratorio(BaseModel):
    __tablename__ = "laboratorio_control_calidad"

    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_laboratorio.id", ondelete="CASCADE"), nullable=False, index=True)
    resultado = Column(String(30), nullable=False)
    motivo_rechazo = Column(String(300), nullable=True)
    observaciones = Column(Text, nullable=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    orden = relationship("OrdenLaboratorio", back_populates="controles_calidad")
