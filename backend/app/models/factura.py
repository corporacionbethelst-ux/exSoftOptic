from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Factura(BaseModel):
    __tablename__ = "facturas"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_facturas_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    moneda = Column(String(3), nullable=False, default="MXN")
    subtotal = Column(Numeric(15, 4), nullable=False)
    impuestos = Column(Numeric(15, 4), nullable=False)
    total = Column(Numeric(15, 4), nullable=False)
    proveedor = Column(String(60), nullable=False, default="MOCK")
    uuid_fiscal = Column(String(80), nullable=True, index=True)
    xml_url = Column(String(500), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    error = Column(Text, nullable=True)
    fecha_timbrado = Column(DateTime(timezone=True), nullable=True)

    lineas = relationship("FacturaLinea", back_populates="factura", cascade="all, delete-orphan")
    eventos = relationship("FacturaEvento", back_populates="factura", cascade="all, delete-orphan")


class FacturaLinea(BaseModel):
    __tablename__ = "facturas_lineas"

    factura_id = Column(UUID(as_uuid=True), ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    descripcion = Column(String(300), nullable=False)
    cantidad = Column(Numeric(15, 3), nullable=False)
    precio_unitario = Column(Numeric(15, 4), nullable=False)
    descuento = Column(Numeric(15, 4), nullable=False, default=0)
    importe = Column(Numeric(15, 4), nullable=False)

    factura = relationship("Factura", back_populates="lineas")


class FacturaEvento(BaseModel):
    __tablename__ = "facturas_eventos"

    factura_id = Column(UUID(as_uuid=True), ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_evento = Column(String(40), nullable=False)
    descripcion = Column(Text, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    factura = relationship("Factura", back_populates="eventos")
