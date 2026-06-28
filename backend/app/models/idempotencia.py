from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel


class IdempotencyKey(BaseModel):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("empresa_id", "scope", "key", name="uq_idempotency_empresa_scope_key"),
    )

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    scope = Column(String(120), nullable=False, index=True)
    key = Column(String(180), nullable=False, index=True)
    request_hash = Column(String(64), nullable=False)
    status = Column(String(30), nullable=False, default="PROCESSING", index=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(JSON, nullable=True)
    attempts = Column(Integer, nullable=False, default=1)
    locked_until = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_error = Column(Text, nullable=True)
