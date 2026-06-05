import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from src.adapters.database.session import session_manager
from src.container import ApplicationContainer
from src.core.settings import settings
from src.infrastructure.messaging.daily_reward_scheduling import schedule_daily_reward_at
from src.drivers.rest import (
    auth,
    users,
    characters,
    items,
    backgrounds,
    transactions,
    user_settings,
    activity_types,
    base_character_activities,
    daily_activities,
    daily_progress,
    food_entries,
    mood_history,
    user_friends,
    character_items,
    character_backgrounds,
    item_categories,
    item_background_positions,
    notifications,
)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    container = ApplicationContainer()
    container.wire(
        packages=["src.drivers.rest"],
        modules=["src.core.auth.admin", "src.core.auth.dependencies"],
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container
        try:
            # Seed daily reward schedule chain (idempotent on DB level).
            now = datetime.now(timezone.utc)
            tomorrow = now.date() + timedelta(days=1)
            next_midnight = datetime(
                tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=timezone.utc
            )
            await schedule_daily_reward_at(
                next_midnight,
                f"daily_reward_seed:{next_midnight.date().isoformat()}:{uuid.uuid4()}",
            )
            yield
        finally:
            container.unwire()
            await session_manager.close()

    app = FastAPI(title="Healthity backend", lifespan=lifespan, version="1.0.0")

    # Custom OpenAPI schema with security schemes
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Healthity Backend API",
            version="1.0.0",
            description="API для управления персонажами, предметами и активностями в игре Healthity",
            routes=app.routes,
        )

        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "TelegramMiniAppAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "Telegram Init Data",
                "description": "Telegram Mini App Init Data. Формат: <init_data>",
            },
            "AdminBasicAuth": {
                "type": "http",
                "scheme": "basic",
                "description": "Admin Basic Authentication. Username: telegram_id, Password: user password",
            },
        }

        # Add security requirements to specific paths
        public_endpoints = ["/catalog", "/users/register"]

        for path, path_item in openapi_schema["paths"].items():
            for _, operation in path_item.items():
                if isinstance(operation, dict) and "operationId" in operation:
                    # Check if this is a public endpoint (no auth required)
                    is_public = any(
                        public_endpoint in path for public_endpoint in public_endpoints
                    )

                    if is_public:
                        # Public endpoints - no security required
                        continue
                    elif "/admin" in path or "admin" in operation.get(
                        "operationId", ""
                    ):
                        # Admin endpoints use Basic Auth
                        operation["security"] = [{"AdminBasicAuth": []}]
                    else:
                        # Regular endpoints use Telegram auth
                        operation["security"] = [{"TelegramMiniAppAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.debug("Request: %s %s", request.method, request.url.path)
        try:
            response = await call_next(request)
            logger.debug("Response status: %s", response.status_code)
            return response
        except Exception:
            logger.exception("Unhandled request failure")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(characters.router, prefix="/api/v1")
    app.include_router(items.router, prefix="/api/v1")
    app.include_router(item_categories.router, prefix="/api/v1")
    app.include_router(backgrounds.router, prefix="/api/v1")
    app.include_router(transactions.router, prefix="/api/v1")
    app.include_router(user_settings.router, prefix="/api/v1")
    app.include_router(activity_types.router, prefix="/api/v1")
    app.include_router(base_character_activities.router, prefix="/api/v1")
    app.include_router(daily_activities.router, prefix="/api/v1")
    app.include_router(daily_progress.router, prefix="/api/v1")
    app.include_router(food_entries.router, prefix="/api/v1")
    app.include_router(mood_history.router, prefix="/api/v1")
    app.include_router(user_friends.router, prefix="/api/v1")
    app.include_router(character_items.router, prefix="/api/v1")
    app.include_router(character_backgrounds.router, prefix="/api/v1")
    app.include_router(item_background_positions.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1")

    return app


app = create_app()
