from sqlalchemy import Column, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CentroCosto(BaseModel):
    __tablename__ = "centros_costo"
    __table_args__ = (UniqueConstraint("empresa_id", "codigo", name="uq_centros_costo_empresa_codigo"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    codigo = Column(String(40), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(500), nullable=True)
    estado = Column(String(30), nullable=False, default="ACTIVO")


class Presupuesto(BaseModel):
    __tablename__ = "presupuestos"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_presupuestos_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    centro_costo_id = Column(UUID(as_uuid=True), ForeignKey("centros_costo.id"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    nombre = Column(String(180), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    observaciones = Column(Text, nullable=True)

    centro_costo = relationship("CentroCosto")
    lineas = relationship("PresupuestoLinea", back_populates="presupuesto", cascade="all, delete-orphan")


class PresupuestoLinea(BaseModel):
    __tablename__ = "presupuestos_lineas"

    presupuesto_id = Column(UUID(as_uuid=True), ForeignKey("presupuestos.id", ondelete="CASCADE"), nullable=False, index=True)
    cuenta_codigo = Column(String(40), nullable=False, index=True)
    monto = Column(Numeric(15, 4), nullable=False)
    monto_comprometido = Column(Numeric(15, 4), nullable=False, default=0)
    monto_ejercido = Column(Numeric(15, 4), nullable=False, default=0)

    presupuesto = relationship("Presupuesto", back_populates="lineas")
