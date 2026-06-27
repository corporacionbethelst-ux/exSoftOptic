from collections.abc import Awaitable, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxEvent
from app.services.outbox_service import OutboxService

OutboxHandler = Callable[[OutboxEvent], Awaitable[None]]


class OutboxDispatcherService:
    """Dispatcher operacional del outbox con handlers inyectables por tipo de evento."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        handlers: dict[str, OutboxHandler],
        retry_delay_seconds: int | None = None,
    ) -> None:
        self.db = db
        self.handlers = handlers
        self.retry_delay_seconds = retry_delay_seconds
        self.outbox = OutboxService(db)

    async def dispatch_pending(self, *, empresa_id: UUID, limit: int = 100) -> dict[str, int]:
        pending = await self.outbox.list_pending(empresa_id=empresa_id, limit=limit)
        dispatched = 0
        failed = 0
        skipped = 0

        for event in pending:
            try:
                processing = await self.outbox.mark_processing(empresa_id=empresa_id, event_id=event.id)
                handler = self.handlers.get(processing.event_type)
                if handler is None:
                    skipped += 1
                    raise ValueError(f"No existe handler para evento {processing.event_type}")
                await handler(processing)
                await self.outbox.mark_published(empresa_id=empresa_id, event_id=processing.id)
                dispatched += 1
            except Exception as exc:
                failed += 1
                await self.outbox.mark_failed(
                    empresa_id=empresa_id,
                    event_id=event.id,
                    error=str(exc),
                    retry_delay_seconds=self.retry_delay_seconds,
                )

        return {"dispatched": dispatched, "failed": failed, "skipped": skipped, "total": len(pending)}
