"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.risk import router as risk_router
from app.config import settings
from app.services.risk_service_adapter import RiskServiceAdapter

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.risk_service_adapter = (
    RiskServiceAdapter.from_roads_file(
        roads_file_path=settings.risk_roads_file,
        road_to_location_json=settings.risk_road_to_location_json,
    )
    if settings.risk_roads_file is not None
    else RiskServiceAdapter()
)
app.include_router(health_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
