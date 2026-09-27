from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import async_session_maker
from app.models.empresa import Empresa
from app.models.outbox import OutboxEvent
from app.services.outbox_dispatcher import OutboxDispatcherService, OutboxHandler

logger = logging.getLogger(__name__)


async def log_domain_event(event: OutboxEvent) -> None:
    """Default integration handler that records dispatch intent until external adapters are configured."""
    logger.info(
        "Dispatching outbox event",
        extra={
            "event_id": str(event.id),
            "event_type": event.event_type,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": event.aggregate_id,
        },
    )


def default_outbox_handlers() -> dict[str, OutboxHandler]:
    """Handlers for currently emitted domain events.

    These handlers make the worker operational today and provide stable extension
    points for replacing each event type with a broker/API adapter later.
    """
    return {
        "VentaConfirmada": log_domain_event,
        "CompraRecibida": log_domain_event,
        "FacturaTimbrada": log_domain_event,
        "FacturaCancelada": log_domain_event,
    }


@dataclass(frozen=True)
class OutboxWorkerConfig:
    poll_interval_seconds: float = 5.0
    batch_size: int = 100


class OutboxWorker:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] = async_session_maker,
        *,
        handlers_factory: Callable[[], dict[str, OutboxHandler]] = default_outbox_handlers,
        config: OutboxWorkerConfig | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.handlers_factory = handlers_factory
        self.config = config or OutboxWorkerConfig()

    async def dispatch_once(self) -> dict[str, int]:
        async with self.session_factory() as session:
            empresa_ids = await self._active_empresa_ids(session)
            totals = {"dispatched": 0, "failed": 0, "skipped": 0, "total": 0, "empresas": len(empresa_ids)}
            for empresa_id in empresa_ids:
                dispatcher = OutboxDispatcherService(session, handlers=self.handlers_factory())
                result = await dispatcher.dispatch_pending(empresa_id=empresa_id, limit=self.config.batch_size)
                for key in ("dispatched", "failed", "skipped", "total"):
                    totals[key] += result[key]
            await session.commit()
            return totals

    async def run_forever(self) -> None:
        while True:
            result = await self.dispatch_once()
            logger.info("Outbox worker cycle completed", extra=result)
            await asyncio.sleep(self.config.poll_interval_seconds)

    async def _active_empresa_ids(self, session: AsyncSession) -> list[UUID]:
        result = await session.execute(select(Empresa.id).where(Empresa.is_active.is_(True)).order_by(Empresa.created_at.asc()))
        return list(result.scalars().all())
