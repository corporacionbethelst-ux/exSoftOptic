from sqlalchemy import Boolean, Column, ForeignKey, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Producto(BaseModel):
    """Catálogo de productos ópticos con soporte de variantes clínicas/comerciales."""
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("empresa_id", "sku", name="uq_productos_empresa_sku"),
        UniqueConstraint("empresa_id", "codigo_barras", name="uq_productos_empresa_codigo_barras"),
    )

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=True)
    marca_id = Column(UUID(as_uuid=True), ForeignKey("marcas.id"), nullable=True)

    sku = Column(String(50), nullable=False, index=True)
    codigo_barras = Column(String(50), nullable=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500), nullable=True)
    tipo_producto = Column(String(50), nullable=False, default="ARMAZON")
    unidad_medida = Column(String(20), default="PIEZA", nullable=False)

    atributos_opticos = Column(JSON, default=dict, nullable=False)
    costo_estandar = Column(Numeric(15, 4), default=0, nullable=False)
    precio_venta = Column(Numeric(15, 4), nullable=False, default=0)
    precio_mayoreo = Column(Numeric(15, 4), nullable=True)

    metodo_costeo = Column(String(20), default="PEPS", nullable=False)
    stock_minimo = Column(Numeric(15, 3), default=0, nullable=False)
    stock_maximo = Column(Numeric(15, 3), default=0, nullable=False)
    punto_reorden = Column(Numeric(15, 3), default=0, nullable=False)

    requiere_receta = Column(Boolean, default=False, nullable=False)
    requiere_lote = Column(Boolean, default=False, nullable=False)
    requiere_serie = Column(Boolean, default=False, nullable=False)
    es_servicio = Column(Boolean, default=False, nullable=False)

    empresa = relationship("Empresa")
    categoria = relationship("Categoria", back_populates="productos")
    marca = relationship("Marca", back_populates="productos")
    existencias = relationship("InventarioExistencia", back_populates="producto")
    movimientos = relationship("KardexMovimiento", back_populates="producto")


class Categoria(BaseModel):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("empresa_id", "nombre", name="uq_categorias_empresa_nombre"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    icono = Column(String(50), nullable=True)
    esta_activa = Column(Boolean, default=True, nullable=False)

    empresa = relationship("Empresa")
    productos = relationship("Producto", back_populates="categoria")


class Marca(BaseModel):
    __tablename__ = "marcas"
    __table_args__ = (UniqueConstraint("empresa_id", "nombre", name="uq_marcas_empresa_nombre"),)

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    esta_activa = Column(Boolean, default=True, nullable=False)

    empresa = relationship("Empresa")
    productos = relationship("Producto", back_populates="marca")
