#!/usr/bin/env python3
"""Run the transactional outbox dispatcher worker."""
from __future__ import annotations

import argparse
import asyncio
import logging

from app.workers.outbox_worker import OutboxWorker, OutboxWorkerConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Dispatch one batch and exit.")
    parser.add_argument("--batch-size", type=int, default=100, help="Max pending events per company per cycle.")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between polling cycles.")
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    worker = OutboxWorker(config=OutboxWorkerConfig(batch_size=args.batch_size, poll_interval_seconds=args.poll_interval))
    if args.once:
        result = await worker.dispatch_once()
        logging.getLogger(__name__).info("Outbox worker one-shot completed", extra=result)
        return
    await worker.run_forever()


if __name__ == "__main__":
    asyncio.run(run())
