import logging

from taskiq import TaskiqScheduler
from taskiq_nats import PullBasedJetStreamBroker
from taskiq_redis import RedisAsyncResultBackend, RedisScheduleSource

from src.core.settings import settings

logger = logging.getLogger(__name__)

# NATS JetStream broker with Redis result backend.
# JetStream guarantees at-least-once delivery and message persistence.
broker = PullBasedJetStreamBroker(
    servers=settings.nats_url,
    queue="healthity-notifications",
).with_result_backend(
    RedisAsyncResultBackend(redis_url=settings.redis.url)
)

# Schedule source backed by Redis: stores ScheduledTask entries as JSON.
# TaskiqScheduler polls this source at each tick and dispatches due tasks.
schedule_source = RedisScheduleSource(url=settings.redis.url)

scheduler = TaskiqScheduler(broker=broker, sources=[schedule_source])
