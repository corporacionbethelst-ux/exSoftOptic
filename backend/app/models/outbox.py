from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import BaseModel


class OutboxEvent(BaseModel):
    __tablename__ = "outbox_events"
    __table_args__ = (
        UniqueConstraint("empresa_id", "idempotency_key", name="uq_outbox_empresa_idempotency_key"),
    )

    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False, index=True)
    aggregate_type = Column(String(120), nullable=False, index=True)
    aggregate_id = Column(String(80), nullable=False, index=True)
    event_type = Column(String(160), nullable=False, index=True)
    payload = Column(JSON, nullable=False, default=dict)
    headers = Column(JSON, nullable=False, default=dict)
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    idempotency_key = Column(String(180), nullable=False)
    available_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
