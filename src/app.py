import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.adapters.database.session import session_manager
from src.container import ApplicationContainer
from src.drivers.rest import (
    users,
    characters,
    items,
    backgrounds,
    transactions,
    user_settings,
    activity_types,
    daily_activities,
    daily_progress,
    mood_history,
    user_friends,
    character_items,
    character_backgrounds,
    item_categories,
    item_background_positions,
)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    container = ApplicationContainer()
    container.wire(packages=["src.drivers.rest", "src.core.auth"])

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.container = container  # type: ignore[attr-defined]
        try:
            yield
        finally:
            container.unwire()
            await session_manager.close()

    app = FastAPI(title="Healthity backend", lifespan=lifespan, version="1.0.0")

    # Middleware для логирования запросов
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.debug(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.debug(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.exception(f"Request failed: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal server error: {str(e)}"},
            )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(characters.router, prefix="/api/v1")
    app.include_router(items.router, prefix="/api/v1")
    app.include_router(item_categories.router, prefix="/api/v1")
    app.include_router(backgrounds.router, prefix="/api/v1")
    app.include_router(transactions.router, prefix="/api/v1")
    app.include_router(user_settings.router, prefix="/api/v1")
    app.include_router(activity_types.router, prefix="/api/v1")
    app.include_router(daily_activities.router, prefix="/api/v1")
    app.include_router(daily_progress.router, prefix="/api/v1")
    app.include_router(mood_history.router, prefix="/api/v1")
    app.include_router(user_friends.router, prefix="/api/v1")
    app.include_router(character_items.router, prefix="/api/v1")
    app.include_router(character_backgrounds.router, prefix="/api/v1")
    app.include_router(item_background_positions.router, prefix="/api/v1")

    return app


app = create_app()
