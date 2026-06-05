import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "healthity_test",
    "DB_USER": "healthity_test",
    "DB_PASSWORD": "healthity_test",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "RABBIT_HOST": "localhost",
    "RABBIT_PORT": "5672",
    "RABBIT_WEB_PORT": "15672",
    "RABBIT_USER": "guest",
    "RABBIT_PASSWORD": "guest",
    "JWT_SECRET_KEY": "test-secret",
    "JWT_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "15",
    "JWT_REFRESH_TOKEN_EXPIRE_MINUTES": "43200",
    "TELEGRAM_BOT_TOKEN": "123456:test-token",
}


for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)
