from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.database.session import session_manager
from src.container import ApplicationContainer


def create_app() -> FastAPI:
    container = ApplicationContainer()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.container = container  # type: ignore[attr-defined]
        try:
            yield
        finally:
            container.unwire()
            await session_manager.close()

    app = FastAPI(title="Healthity backend", lifespan=lifespan, version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()
