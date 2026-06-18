# backend/app/models/usuario.py (verificar relaciones)
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
import uuid
from datetime import datetime


class Rol(BaseModel):
    __tablename__ = "roles"
    
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(500))
    es_sistema = Column(Boolean, default=False)
    permisos = Column(JSON, default=list)
    nivel_acceso = Column(Integer, default=1)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(BaseModel):
    __tablename__ = "usuarios"
    
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    telefono = Column(String(20))
    avatar_url = Column(String(500))
    
    rol_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"))
    
    esta_activo = Column(Boolean, default=True)
    email_verificado = Column(Boolean, default=False)
    mfa_habilitado = Column(Boolean, default=False)
    mfa_secret = Column(String(32))
    ultimo_acceso = Column(DateTime(timezone=True))
    intentos_fallidos = Column(Integer, default=0)
    bloqueado_hasta = Column(DateTime(timezone=True))
    preferencias = Column(JSON, default=dict)
    
    # Relaciones
    rol = relationship("Rol", back_populates="usuarios")
    sucursal = relationship("Sucursal", back_populates="usuarios")
    empresa = relationship("Empresa", back_populates="usuarios")
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")


class Sesion(BaseModel):
    __tablename__ = "sesiones"
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    refresh_token_hash = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    dispositivo = Column(String(100))
    ubicacion = Column(String(200))
    expira_en = Column(DateTime(timezone=True), nullable=False)
    es_activa = Column(Boolean, default=True)
    ultima_actividad = Column(DateTime(timezone=True))
    
    usuario = relationship("Usuario", back_populates="sesiones")