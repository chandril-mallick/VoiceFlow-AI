"""
VoiceFlow AI — FastAPI Application
Main entry point with lifespan events, router registration, and middleware setup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.middleware import setup_middleware
from src.core.redis import close_redis

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting %s (env=%s)", settings.app_name, settings.app_env)
    logger.info("📦 Database: %s", settings.postgres_host)
    logger.info("📦 Redis: %s:%s", settings.redis_host, settings.redis_port)
    logger.info("📦 Qdrant: %s", settings.qdrant_url)
    logger.info("🤖 Ollama: %s (%s)", settings.ollama_base_url, settings.ollama_model)

    yield

    # Shutdown
    logger.info("🛑 Shutting down %s", settings.app_name)
    await close_redis()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered multilingual voice sales agent platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ──
    setup_middleware(app)

    # ── Routers ──
    from src.auth.router import router as auth_router
    from src.crm.router import router as crm_router
    from src.rag.router import router as rag_router
    from src.api.websocket import router as ws_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(crm_router, prefix="/api/v1")
    app.include_router(rag_router, prefix="/api/v1")
    app.include_router(ws_router)

    # ── Health Check ──
    @app.get("/api/v1/health", tags=["System"])
    async def health_check():
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": "1.0.0",
            "env": settings.app_env,
        }

    # ── Global Exception Handler ──
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()
