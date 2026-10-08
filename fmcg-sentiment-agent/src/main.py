import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.logging_config import configure_logging
from src.config.settings import API_TITLE, API_VERSION
from src.exceptions.handlers import register_exception_handlers
from src.routers import (
    health_router, trends_router, flagged_router, overview_router,
    assistant_router, audit_router, dashboard_router,
)
from src.services.agent_service import close_runtimes, get_runtime

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app):
    logger.info("Starting the assistant.")
    get_runtime()
    yield
    logger.info("Shutting down the assistant.")
    close_runtimes()

app = FastAPI(title=API_TITLE, version=API_VERSION, lifespan=lifespan)

register_exception_handlers(app)

app.include_router(health_router.router)
app.include_router(trends_router.router)
app.include_router(flagged_router.router)
app.include_router(overview_router.router)
app.include_router(assistant_router.router)
app.include_router(audit_router.router)
app.include_router(dashboard_router.router)
