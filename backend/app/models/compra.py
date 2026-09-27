from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Proveedor(BaseModel):
    __tablename__ = "proveedores"
    __table_args__ = (UniqueConstraint("empresa_id", "rfc", name="uq_proveedores_empresa_rfc"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    rfc = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    telefono = Column(String(30), nullable=True)

    ordenes = relationship("OrdenCompra", back_populates="proveedor")


class OrdenCompra(BaseModel):
    __tablename__ = "ordenes_compra"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_oc_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores.id"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    subtotal = Column(Numeric(15, 4), nullable=False, default=0)
    impuestos = Column(Numeric(15, 4), nullable=False, default=0)
    total = Column(Numeric(15, 4), nullable=False, default=0)

    proveedor = relationship("Proveedor", back_populates="ordenes")
    lineas = relationship("OrdenCompraLinea", back_populates="orden", cascade="all, delete-orphan")
    recepciones = relationship("RecepcionCompra", back_populates="orden", cascade="all, delete-orphan")


class OrdenCompraLinea(BaseModel):
    __tablename__ = "ordenes_compra_lineas"

    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_compra.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    descripcion = Column(String(300), nullable=False)
    cantidad = Column(Numeric(15, 3), nullable=False)
    cantidad_recibida = Column(Numeric(15, 3), nullable=False, default=0)
    costo_unitario = Column(Numeric(15, 4), nullable=False)
    importe = Column(Numeric(15, 4), nullable=False)

    orden = relationship("OrdenCompra", back_populates="lineas")
    producto = relationship("Producto")


class RecepcionCompra(BaseModel):
    __tablename__ = "recepciones_compra"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_recepcion_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    orden_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_compra.id"), nullable=False, index=True)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True)
    folio = Column(String(40), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estado = Column(String(30), nullable=False, default="RECIBIDA")
    total = Column(Numeric(15, 4), nullable=False, default=0)

    orden = relationship("OrdenCompra", back_populates="recepciones")
    lineas = relationship("RecepcionCompraLinea", back_populates="recepcion", cascade="all, delete-orphan")


class RecepcionCompraLinea(BaseModel):
    __tablename__ = "recepciones_compra_lineas"

    recepcion_id = Column(UUID(as_uuid=True), ForeignKey("recepciones_compra.id", ondelete="CASCADE"), nullable=False, index=True)
    orden_linea_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_compra_lineas.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Numeric(15, 3), nullable=False)
    costo_unitario = Column(Numeric(15, 4), nullable=False)
    importe = Column(Numeric(15, 4), nullable=False)
    lote = Column(String(80), nullable=True)
    numero_serie = Column(String(120), nullable=True)

    recepcion = relationship("RecepcionCompra", back_populates="lineas")
    orden_linea = relationship("OrdenCompraLinea")
    producto = relationship("Producto")


class SolicitudCompra(BaseModel):
    __tablename__ = "solicitudes_compra"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_solicitudes_compra_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    folio = Column(String(40), nullable=False)
    origen = Column(String(40), nullable=False, default="STOCK_MINIMO")
    estado = Column(String(30), nullable=False, default="BORRADOR")
    observaciones = Column(String(500), nullable=True)

    lineas = relationship("SolicitudCompraLinea", back_populates="solicitud", cascade="all, delete-orphan")


class SolicitudCompraLinea(BaseModel):
    __tablename__ = "solicitudes_compra_lineas"

    solicitud_id = Column(UUID(as_uuid=True), ForeignKey("solicitudes_compra.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    cantidad_sugerida = Column(Numeric(15, 3), nullable=False)
    costo_estimado = Column(Numeric(15, 4), nullable=False, default=0)
    motivo = Column(String(250), nullable=False)

    solicitud = relationship("SolicitudCompra", back_populates="lineas")
    producto = relationship("Producto")
