from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OutboxEventCreate(BaseModel):
    aggregate_type: str = Field(..., min_length=1, max_length=120)
    aggregate_id: str = Field(..., min_length=1, max_length=80)
    event_type: str = Field(..., min_length=1, max_length=160)
    payload: dict = Field(default_factory=dict)
    headers: dict = Field(default_factory=dict)
    idempotency_key: str | None = Field(None, max_length=180)
    available_at: datetime | None = None
    max_attempts: int = Field(default=5, ge=1, le=50)


class OutboxEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict
    headers: dict
    status: str
    attempts: int
    max_attempts: int
    idempotency_key: str
    available_at: datetime
    locked_at: datetime | None
    published_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime


class OutboxEventFailRequest(BaseModel):
    error: str = Field(..., min_length=1, max_length=2000)
    retry_delay_seconds: int = Field(default=60, ge=0, le=86_400)
