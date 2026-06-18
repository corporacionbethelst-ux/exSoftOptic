# backend/app/models/producto.py
from sqlalchemy import Column, String, Numeric, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import uuid


class Producto(BaseModel):
    """Modelo de productos - versión corregida con UUID en todas las FKs"""
    __tablename__ = "productos"
    
    # Foreign Keys - TODAS deben ser UUID para coincidir con los IDs
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=True)
    marca_id = Column(UUID(as_uuid=True), ForeignKey("marcas.id"), nullable=True)
    
    # Información básica
    sku = Column(String(50), nullable=False, unique=True)
    codigo_barras = Column(String(50), unique=True, nullable=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(String(500), nullable=True)
    tipo_producto = Column(String(50), nullable=False, default="PRODUCTO")
    unidad_medida = Column(String(20), default="PIEZA")
    
    # Precios
    costo_estandar = Column(Numeric(15, 2), default=0)
    precio_venta = Column(Numeric(15, 2), nullable=False, default=0)
    precio_mayoreo = Column(Numeric(15, 2), nullable=True)
    
    # Inventario
    metodo_costeo = Column(String(20), default="PROMEDIO")
    stock_minimo = Column(Numeric(15, 3), default=0)
    stock_maximo = Column(Numeric(15, 3), default=0)
    punto_reorden = Column(Numeric(15, 3), default=0)
    
    # Control
    requiere_receta = Column(Boolean, default=False)
    es_servicio = Column(Boolean, default=False)
    
    # Relaciones
    empresa = relationship("Empresa")


class Categoria(BaseModel):
    """Categorías de productos"""
    __tablename__ = "categorias"
    
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    icono = Column(String(50), nullable=True)
    esta_activa = Column(Boolean, default=True)
    
    empresa = relationship("Empresa")


class Marca(BaseModel):
    """Marcas de productos"""
    __tablename__ = "marcas"
    
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    esta_activa = Column(Boolean, default=True)
    
    empresa = relationship("Empresa")