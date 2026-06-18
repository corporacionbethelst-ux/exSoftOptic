# backend/app/models/sucursal.py
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import uuid


class Sucursal(BaseModel):
    __tablename__ = "sucursales"
    
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    codigo = Column(String(10), nullable=False)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(500))
    telefono = Column(String(20))
    email = Column(String(100))
    rfc = Column(String(20))
    codigo_postal = Column(String(10))
    ciudad = Column(String(100))
    estado = Column(String(100))
    pais = Column(String(50), default="México")
    es_principal = Column(Boolean, default=False)
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="sucursales")
    usuarios = relationship("Usuario", back_populates="sucursal")