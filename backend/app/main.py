from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import create_db_and_tables
from app.routers import sampling, statistics


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Medical Device Statistics",
        version=settings.app_version,
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "app_version": settings.app_version,
            "algorithm_version": settings.algorithm_version,
        }

    app.include_router(sampling.router)
    app.include_router(statistics.router)

    return app


app = create_app()
