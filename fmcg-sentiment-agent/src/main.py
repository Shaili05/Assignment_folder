from fastapi import FastAPI

from src.config.logging_config import configure_logging
from src.config.settings import API_TITLE, API_VERSION
from src.routers import (
    health_router, trends_router, flagged_router, overview_router,
    assistant_router, audit_router, dashboard_router,
)
from src.services.agent_service import get_runtime

configure_logging()

app = FastAPI(title=API_TITLE, version=API_VERSION)

app.include_router(health_router.router)
app.include_router(trends_router.router)
app.include_router(flagged_router.router)
app.include_router(overview_router.router)
app.include_router(assistant_router.router)
app.include_router(audit_router.router)
app.include_router(dashboard_router.router)


@app.on_event("startup")
def warm_up_assistant():
    get_runtime()
