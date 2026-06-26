from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class Cliente(BaseModel):
    __tablename__ = "clientes"
    __table_args__ = (UniqueConstraint("empresa_id", "email", name="uq_clientes_empresa_email"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(150), nullable=True, index=True)
    telefono = Column(String(30), nullable=True)
    rfc = Column(String(20), nullable=True)
    codigo_postal = Column(String(10), nullable=True)
    regimen_fiscal = Column(String(50), nullable=True)

    pacientes = relationship("Paciente", back_populates="cliente")
    ventas = relationship("Venta", back_populates="cliente")


class Paciente(BaseModel):
    __tablename__ = "pacientes"

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    telefono = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    cliente = relationship("Cliente", back_populates="pacientes")
    recetas = relationship("RecetaOptica", back_populates="paciente")
    ventas = relationship("Venta", back_populates="paciente")


class RecetaOptica(BaseModel):
    __tablename__ = "recetas_opticas"

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False)
    od_esfera = Column(Numeric(5, 2), nullable=True)
    od_cilindro = Column(Numeric(5, 2), nullable=True)
    od_eje = Column(Numeric(5, 2), nullable=True)
    od_adicion = Column(Numeric(5, 2), nullable=True)
    oi_esfera = Column(Numeric(5, 2), nullable=True)
    oi_cilindro = Column(Numeric(5, 2), nullable=True)
    oi_eje = Column(Numeric(5, 2), nullable=True)
    oi_adicion = Column(Numeric(5, 2), nullable=True)
    dnp = Column(Numeric(5, 2), nullable=True)
    altura = Column(Numeric(5, 2), nullable=True)
    observaciones = Column(Text, nullable=True)

    paciente = relationship("Paciente", back_populates="recetas")
    ventas = relationship("Venta", back_populates="receta")


class Venta(BaseModel):
    __tablename__ = "ventas"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_ventas_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False, index=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey("pacientes.id"), nullable=True, index=True)
    receta_id = Column(UUID(as_uuid=True), ForeignKey("recetas_opticas.id"), nullable=True)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True)
    folio = Column(String(40), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estado = Column(String(30), nullable=False, default="BORRADOR")
    subtotal = Column(Numeric(15, 4), nullable=False, default=0)
    impuestos = Column(Numeric(15, 4), nullable=False, default=0)
    total = Column(Numeric(15, 4), nullable=False, default=0)
    costo_total = Column(Numeric(15, 4), nullable=False, default=0)

    cliente = relationship("Cliente", back_populates="ventas")
    paciente = relationship("Paciente", back_populates="ventas")
    receta = relationship("RecetaOptica", back_populates="ventas")
    lineas = relationship("VentaLinea", back_populates="venta", cascade="all, delete-orphan")
    pagos = relationship("PagoVenta", back_populates="venta", cascade="all, delete-orphan")


class VentaLinea(BaseModel):
    __tablename__ = "ventas_lineas"

    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    descripcion = Column(String(300), nullable=False)
    cantidad = Column(Numeric(15, 3), nullable=False)
    precio_unitario = Column(Numeric(15, 4), nullable=False)
    descuento = Column(Numeric(15, 4), nullable=False, default=0)
    importe = Column(Numeric(15, 4), nullable=False)
    costo_total = Column(Numeric(15, 4), nullable=False, default=0)

    venta = relationship("Venta", back_populates="lineas")
    producto = relationship("Producto")


class PagoVenta(BaseModel):
    __tablename__ = "ventas_pagos"

    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False, index=True)
    metodo_pago = Column(String(40), nullable=False)
    monto = Column(Numeric(15, 4), nullable=False)
    referencia = Column(String(120), nullable=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    venta = relationship("Venta", back_populates="pagos")


class DevolucionVenta(BaseModel):
    __tablename__ = "ventas_devoluciones"
    __table_args__ = (UniqueConstraint("empresa_id", "folio", name="uq_devoluciones_venta_empresa_folio"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    venta_id = Column(UUID(as_uuid=True), ForeignKey("ventas.id"), nullable=False, index=True)
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True)
    folio = Column(String(40), nullable=False)
    motivo = Column(String(250), nullable=False)
    estado = Column(String(30), nullable=False, default="CONFIRMADA")
    subtotal = Column(Numeric(15, 4), nullable=False, default=0)
    impuestos = Column(Numeric(15, 4), nullable=False, default=0)
    total = Column(Numeric(15, 4), nullable=False, default=0)
    costo_total = Column(Numeric(15, 4), nullable=False, default=0)

    venta = relationship("Venta")
    lineas = relationship("DevolucionVentaLinea", back_populates="devolucion", cascade="all, delete-orphan")


class DevolucionVentaLinea(BaseModel):
    __tablename__ = "ventas_devoluciones_lineas"

    devolucion_id = Column(UUID(as_uuid=True), ForeignKey("ventas_devoluciones.id", ondelete="CASCADE"), nullable=False, index=True)
    venta_linea_id = Column(UUID(as_uuid=True), ForeignKey("ventas_lineas.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Numeric(15, 3), nullable=False)
    importe = Column(Numeric(15, 4), nullable=False)
    costo_total = Column(Numeric(15, 4), nullable=False, default=0)

    devolucion = relationship("DevolucionVenta", back_populates="lineas")
    venta_linea = relationship("VentaLinea")
    producto = relationship("Producto")
