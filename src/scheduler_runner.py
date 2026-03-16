"""
Taskiq scheduler entry point.

Run with:
    python -m src.scheduler_runner

The scheduler polls RedisScheduleSource at each cron tick and dispatches
due ScheduledTask entries to NATS so workers can pick them up.
"""

import asyncio
import logging

from taskiq.scheduler import TaskiqScheduler

from src.infrastructure.messaging.broker import broker, scheduler

# Task modules must be imported so the scheduler knows the task names.
import src.infrastructure.tasks.notifications  # noqa: F401

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting Taskiq scheduler …")

    await broker.startup()
    try:
        await scheduler.startup()
    finally:
        await broker.shutdown()
        logger.info("Scheduler shut down.")


if __name__ == "__main__":
    asyncio.run(main())
