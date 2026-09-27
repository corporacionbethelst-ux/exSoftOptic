#!/usr/bin/env python3
"""Clean operational tables with tenant-scoped retention controls."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.database import async_session_maker
from app.services.idempotency_service import IdempotencyService
from app.services.outbox_service import OutboxService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--empresa-id", required=True, type=UUID, help="Tenant/company UUID to clean.")
    parser.add_argument("--idempotency-limit", type=int, default=500, help="Max expired idempotency rows to delete.")
    parser.add_argument("--outbox-limit", type=int, default=500, help="Max outbox rows to process per cleanup category.")
    parser.add_argument("--outbox-published-days", type=int, default=30, help="Delete published outbox events older than this many days.")
    parser.add_argument("--processing-timeout-minutes", type=int, default=15, help="Release PROCESSING outbox events locked longer than this many minutes.")
    return parser.parse_args()


async def cleanup() -> dict[str, int | str]:
    args = parse_args()
    now = datetime.now(timezone.utc)
    async with async_session_maker() as session:
        idempotency_deleted = await IdempotencyService(session).cleanup_expired(
            empresa_id=args.empresa_id,
            older_than=now,
            limit=args.idempotency_limit,
        )
        outbox_service = OutboxService(session)
        outbox_released = await outbox_service.release_stale_processing(
            empresa_id=args.empresa_id,
            older_than=now - timedelta(minutes=args.processing_timeout_minutes),
            limit=args.outbox_limit,
        )
        outbox_deleted = await outbox_service.cleanup_published(
            empresa_id=args.empresa_id,
            older_than=now - timedelta(days=args.outbox_published_days),
            limit=args.outbox_limit,
        )
        await session.commit()
    return {
        "empresa_id": str(args.empresa_id),
        "idempotency_deleted": idempotency_deleted,
        "outbox_released": outbox_released,
        "outbox_deleted": outbox_deleted,
    }


def main() -> int:
    result = asyncio.run(cleanup())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
