# backend/app/models/empresa.py
from sqlalchemy import Column, String, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import uuid


class Empresa(BaseModel):
    __tablename__ = "empresas"
    
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(150))
    rfc = Column(String(20), unique=True, nullable=False)
    regimen_fiscal = Column(String(50), nullable=False)
    codigo_postal = Column(String(10), nullable=False)
    representante_legal = Column(String(150))
    logo_url = Column(String(500))
    configuracion_contable = Column(JSON, default=dict)
    serie_factura = Column(String(10), default="A")
    folio_actual = Column(Integer, default=0)
    moneda_base = Column(String(3), default="MXN")
    
    # Relaciones
    sucursales = relationship("Sucursal", back_populates="empresa", cascade="all, delete-orphan")
    usuarios = relationship("Usuario", back_populates="empresa", cascade="all, delete-orphan")