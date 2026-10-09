"""Road risk and demo observation endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.risk_service_adapter import (
    ObservationConflict,
    RiskServiceAdapter,
    RiskServiceNotConfigured,
    RoadNotFound,
)

router = APIRouter(tags=["risk"])


class RainfallObservationPayload(BaseModel):
    """Input accepted by the in-memory demo/testing observation endpoint."""

    model_config = ConfigDict(extra="forbid")

    location_id: str = Field(min_length=1)
    timestamp: datetime
    rainfall_intensity_mm_hr: float = Field(ge=0)
    is_raining: bool | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accumulated_rainfall_mm: float | None = Field(default=None, ge=0)
    source: str = "manual"

    @field_validator("location_id")
    @classmethod
    def location_id_must_not_be_whitespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("location_id must not be empty")
        return value

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone")
        return value


def get_risk_service(request: Request) -> RiskServiceAdapter:
    return request.app.state.risk_service_adapter


def _as_of(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise HTTPException(status_code=422, detail="as_of must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HTTPException(status_code=422, detail="as_of must include a timezone")
    return parsed


def _translate_service_error(error: Exception) -> HTTPException:
    if isinstance(error, RiskServiceNotConfigured):
        return HTTPException(status_code=503, detail="Risk service is not configured")
    if isinstance(error, RoadNotFound):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, ObservationConflict):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, (ValueError, TypeError)):
        return HTTPException(status_code=422, detail=str(error))
    raise error


@router.get("/roads/risk", summary="Get risk for all configured roads")
def get_all_roads_risk(
    as_of: str | None = None,
    service: RiskServiceAdapter = Depends(get_risk_service),
) -> dict[str, Any]:
    """Static collection route; kept before the dynamic road-ID route."""
    timestamp = _as_of(as_of)
    try:
        roads = service.get_all_roads_risk(as_of=timestamp)
    except Exception as error:
        raise _translate_service_error(error) from error
    return {"roads": roads, "count": len(roads)}


@router.get("/roads/{road_id}/risk", summary="Get risk for one configured road")
def get_road_risk(
    road_id: str,
    as_of: str | None = None,
    service: RiskServiceAdapter = Depends(get_risk_service),
) -> dict[str, Any]:
    timestamp = _as_of(as_of)
    try:
        return service.get_road_risk(road_id=road_id, as_of=timestamp)
    except Exception as error:
        raise _translate_service_error(error) from error


@router.post("/observations", summary="Ingest a demo rainfall observation")
def ingest_observation(
    payload: RainfallObservationPayload,
    service: RiskServiceAdapter = Depends(get_risk_service),
) -> dict[str, Any]:
    """Update in-memory M3 state only; this is not a live or persistent feed."""
    observation = payload.model_dump(mode="json", exclude_none=True)
    try:
        return service.ingest_observation(observation)
    except Exception as error:
        raise _translate_service_error(error) from error
