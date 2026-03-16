"""
Taskiq worker entry point.

Run with:
    taskiq worker src.worker:broker --tasks-pattern "src/infrastructure/tasks/*.py"

The --tasks-pattern flag ensures that task modules are auto-discovered and
registered before the worker starts consuming messages from NATS.
"""

# Import broker first so Taskiq knows which broker to bind tasks to.
from src.infrastructure.messaging.broker import broker  # noqa: F401

# Explicitly import the task module so the @broker.task decorator runs
# and registers send_notification_task with this broker instance.
import src.infrastructure.tasks.notifications  # noqa: F401
