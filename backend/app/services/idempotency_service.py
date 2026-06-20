import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotencia import IdempotencyKey


@dataclass(frozen=True)
class IdempotencyStartResult:
    record: IdempotencyKey
    replay: bool


class IdempotencyService:
    """Control transaccional de idempotencia para endpoints críticos reintentables."""

    STATUS_PROCESSING = "PROCESSING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start(
        self,
        *,
        empresa_id: UUID,
        scope: str,
        key: str,
        request_payload: dict,
        ttl_hours: int = 24,
        lock_seconds: int = 120,
    ) -> IdempotencyStartResult:
        request_hash = self.hash_payload(request_payload)
        result = await self.db.execute(
            select(IdempotencyKey)
            .where(IdempotencyKey.empresa_id == empresa_id, IdempotencyKey.scope == scope, IdempotencyKey.key == key)
            .with_for_update()
        )
        record = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if record is None:
            record = IdempotencyKey(
                empresa_id=empresa_id,
                scope=scope,
                key=key,
                request_hash=request_hash,
                status=self.STATUS_PROCESSING,
                locked_until=now + timedelta(seconds=lock_seconds),
                expires_at=now + timedelta(hours=ttl_hours),
            )
            self.db.add(record)
            await self.db.flush()
            return IdempotencyStartResult(record=record, replay=False)

        if record.request_hash != request_hash:
            raise ValueError("Idempotency-Key reutilizada con payload distinto")
        if record.status == self.STATUS_COMPLETED:
            return IdempotencyStartResult(record=record, replay=True)
        if record.locked_until and record.locked_until > now and record.status == self.STATUS_PROCESSING:
            raise ValueError("Solicitud idempotente aún en procesamiento")

        record.status = self.STATUS_PROCESSING
        record.locked_until = now + timedelta(seconds=lock_seconds)
        record.attempts += 1
        record.last_error = None
        await self.db.flush()
        return IdempotencyStartResult(record=record, replay=False)

    async def complete(self, *, record: IdempotencyKey, response_status: int, response_body: dict) -> IdempotencyKey:
        record.status = self.STATUS_COMPLETED
        record.response_status = response_status
        record.response_body = response_body
        record.completed_at = datetime.now(timezone.utc)
        record.locked_until = None
        record.last_error = None
        await self.db.flush()
        return record

    async def fail(self, *, record: IdempotencyKey, error: str) -> IdempotencyKey:
        record.status = self.STATUS_FAILED
        record.last_error = error[:2000]
        record.locked_until = None
        await self.db.flush()
        return record

    def hash_payload(self, payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
