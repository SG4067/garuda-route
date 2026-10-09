"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.risk import router as risk_router
from app.config import settings
from app.services.risk_service_adapter import RiskServiceAdapter

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.risk_service_adapter = RiskServiceAdapter()
app.include_router(health_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
