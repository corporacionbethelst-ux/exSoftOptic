from sqlalchemy import Column, Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class InventarioExistencia(BaseModel):
    __tablename__ = "inventario_existencias"
    __table_args__ = (
        UniqueConstraint("empresa_id", "sucursal_id", "producto_id", name="uq_existencia_empresa_sucursal_producto"),
    )

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    cantidad = Column(Numeric(15, 3), nullable=False, default=0)
    costo_promedio = Column(Numeric(15, 4), nullable=False, default=0)
    valor_total = Column(Numeric(15, 4), nullable=False, default=0)

    producto = relationship("Producto", back_populates="existencias")
    sucursal = relationship("Sucursal")


class CapaInventario(BaseModel):
    __tablename__ = "inventario_capas"
    __table_args__ = (Index("ix_capas_peps", "empresa_id", "sucursal_id", "producto_id", "created_at"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    lote = Column(String(80), nullable=True)
    numero_serie = Column(String(120), nullable=True)
    fecha_caducidad = Column(Date, nullable=True)
    cantidad_inicial = Column(Numeric(15, 3), nullable=False)
    cantidad_disponible = Column(Numeric(15, 3), nullable=False)
    costo_unitario = Column(Numeric(15, 4), nullable=False)
    referencia = Column(String(120), nullable=True)


class KardexMovimiento(BaseModel):
    __tablename__ = "kardex_movimientos"
    __table_args__ = (Index("ix_kardex_producto_fecha", "empresa_id", "producto_id", "created_at"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False, index=True)
    tipo_movimiento = Column(String(30), nullable=False)
    origen = Column(String(80), nullable=False)
    referencia = Column(String(120), nullable=True)
    cantidad = Column(Numeric(15, 3), nullable=False)
    costo_unitario = Column(Numeric(15, 4), nullable=False)
    costo_total = Column(Numeric(15, 4), nullable=False)
    saldo_cantidad = Column(Numeric(15, 3), nullable=False)
    saldo_valor = Column(Numeric(15, 4), nullable=False)
    lote = Column(String(80), nullable=True)
    numero_serie = Column(String(120), nullable=True)

    producto = relationship("Producto", back_populates="movimientos")
    asiento_id = Column(UUID(as_uuid=True), ForeignKey("asientos_contables.id"), nullable=True)
