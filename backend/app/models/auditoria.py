from sqlalchemy import Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class AuditoriaEvento(BaseModel):
    __tablename__ = "auditoria_eventos"

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True, index=True)
    secuencia = Column(Integer, nullable=False, index=True)
    accion = Column(String(80), nullable=False, index=True)
    entidad = Column(String(120), nullable=False, index=True)
    entidad_id = Column(String(80), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    payload = Column(JSON, nullable=False, default=dict)
    previous_hash = Column(String(64), nullable=True)
    event_hash = Column(String(64), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
