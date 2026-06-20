from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxEvent
from app.schemas.outbox import OutboxEventCreate


class OutboxService:
    """Outbox transaccional para publicar eventos de dominio de forma confiable."""

    STATUS_PENDING = "PENDING"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_PUBLISHED = "PUBLISHED"
    STATUS_FAILED = "FAILED"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def enqueue(self, *, empresa_id: UUID, payload: OutboxEventCreate) -> OutboxEvent:
        idempotency_key = payload.idempotency_key or self._default_idempotency_key(payload)
        existing = await self.get_by_idempotency_key(empresa_id=empresa_id, idempotency_key=idempotency_key)
        if existing:
            return existing

        event = OutboxEvent(
            empresa_id=empresa_id,
            aggregate_type=payload.aggregate_type,
            aggregate_id=payload.aggregate_id,
            event_type=payload.event_type,
            payload=payload.payload,
            headers=payload.headers,
            idempotency_key=idempotency_key,
            available_at=payload.available_at or datetime.now(timezone.utc),
            max_attempts=payload.max_attempts,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_by_idempotency_key(self, *, empresa_id: UUID, idempotency_key: str) -> OutboxEvent | None:
        result = await self.db.execute(
            select(OutboxEvent).where(
                OutboxEvent.empresa_id == empresa_id,
                OutboxEvent.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def list_pending(self, *, empresa_id: UUID, limit: int = 100) -> list[OutboxEvent]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(OutboxEvent)
            .where(
                OutboxEvent.empresa_id == empresa_id,
                OutboxEvent.status == self.STATUS_PENDING,
                OutboxEvent.available_at <= now,
                OutboxEvent.attempts < OutboxEvent.max_attempts,
            )
            .order_by(OutboxEvent.available_at.asc(), OutboxEvent.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_processing(self, *, empresa_id: UUID, event_id: UUID) -> OutboxEvent:
        event = await self._get_scoped(empresa_id=empresa_id, event_id=event_id, lock=True)
        if event.status not in {self.STATUS_PENDING, self.STATUS_FAILED}:
            raise ValueError("El evento no está disponible para procesamiento")
        if event.attempts >= event.max_attempts:
            raise ValueError("El evento agotó sus reintentos")
        event.status = self.STATUS_PROCESSING
        event.attempts += 1
        event.locked_at = datetime.now(timezone.utc)
        event.last_error = None
        await self.db.flush()
        return event

    async def mark_published(self, *, empresa_id: UUID, event_id: UUID) -> OutboxEvent:
        event = await self._get_scoped(empresa_id=empresa_id, event_id=event_id, lock=True)
        event.status = self.STATUS_PUBLISHED
        event.published_at = datetime.now(timezone.utc)
        event.locked_at = None
        event.last_error = None
        await self.db.flush()
        return event

    async def mark_failed(self, *, empresa_id: UUID, event_id: UUID, error: str, retry_delay_seconds: int = 60) -> OutboxEvent:
        event = await self._get_scoped(empresa_id=empresa_id, event_id=event_id, lock=True)
        event.last_error = error[:2000]
        event.locked_at = None
        if event.attempts >= event.max_attempts:
            event.status = self.STATUS_FAILED
        else:
            event.status = self.STATUS_PENDING
            event.available_at = datetime.now(timezone.utc) + timedelta(seconds=retry_delay_seconds)
        await self.db.flush()
        return event

    async def _get_scoped(self, *, empresa_id: UUID, event_id: UUID, lock: bool = False) -> OutboxEvent:
        query = select(OutboxEvent).where(OutboxEvent.empresa_id == empresa_id, OutboxEvent.id == event_id)
        if lock:
            query = query.with_for_update()
        result = await self.db.execute(query)
        event = result.scalar_one_or_none()
        if event is None:
            raise ValueError("Evento outbox no encontrado")
        return event

    def _default_idempotency_key(self, payload: OutboxEventCreate) -> str:
        return f"{payload.aggregate_type}:{payload.aggregate_id}:{payload.event_type}"
