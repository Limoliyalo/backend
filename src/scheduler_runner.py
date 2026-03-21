"""
Taskiq scheduler entry point.

Must use the same logic as `taskiq scheduler` CLI: `TaskiqScheduler.startup()`
does NOT run the polling loop — only `run_scheduler()` from taskiq does
(`run_scheduler_loop` + RedisScheduleSource.startup).

Run:
    python -m src.scheduler_runner

Or equivalently:
    taskiq scheduler src.infrastructure.messaging.broker:scheduler -fsd \\
      --tasks-pattern "src/infrastructure/tasks/*.py"
"""

import asyncio
import sys

from taskiq.cli.scheduler.args import SchedulerArgs
from taskiq.cli.scheduler.run import run_scheduler


def main() -> None:
    argv = [
        "src.infrastructure.messaging.broker:scheduler",
        "-fsd",
        "--tasks-pattern",
        "src/infrastructure/tasks/*.py",
    ]
    args = SchedulerArgs.from_cli(argv)
    try:
        asyncio.run(run_scheduler(args))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
