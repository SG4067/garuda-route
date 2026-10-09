"""Thin adapter for M3's public ``WaterloggingRiskService`` facade.

This layer delegates risk calculations and observation ingestion to M3. It only
normalizes service exceptions and works around the current single-road
unmapped exception by returning the matching batch assessment. The latter can
be removed once the coordinated M3 change returns UNMAPPED directly.
"""

from datetime import datetime
from typing import Any


class RiskServiceNotConfigured(RuntimeError):
    """No M3 service instance has been installed in the application."""


class RoadNotFound(Exception):
    """The requested road ID is not present in M3's configured roads."""


class ObservationConflict(Exception):
    """M3 rejected a conflicting observation for an existing timestamp."""


def _exception_named(error: Exception, name: str) -> bool:
    """Avoid importing M3 internals while still translating its public errors."""
    return any(cls.__name__ == name for cls in type(error).__mro__)


class RiskServiceAdapter:
    """Delegate to an injected M3 facade without reimplementing risk logic."""

    def __init__(self, implementation: object | None = None) -> None:
        self._implementation = implementation

    @property
    def is_configured(self) -> bool:
        return self._implementation is not None

    def _service(self) -> Any:
        if self._implementation is None:
            raise RiskServiceNotConfigured("M3 WaterloggingRiskService is not configured")
        return self._implementation

    def get_all_roads_risk(self, as_of: datetime | None = None) -> list[dict[str, Any]]:
        return self._service().get_all_roads_risk(as_of=as_of)

    def get_road_risk(self, road_id: str, as_of: datetime | None = None) -> dict[str, Any]:
        service = self._service()
        try:
            return service.get_road_risk(road_id=road_id, as_of=as_of)
        except Exception as error:
            if _exception_named(error, "RoadNotFoundError"):
                raise RoadNotFound(str(error)) from error
            if not _exception_named(error, "RoadMappingNotFoundError"):
                raise

        # M3's collection method already emits an UNKNOWN / UNMAPPED assessment.
        # Reuse that exact object to keep single and collection semantics equal.
        for assessment in service.get_all_roads_risk(as_of=as_of):
            if assessment.get("road_id") == road_id:
                return assessment
        raise RoadNotFound(f"Road ID '{road_id}' was not found")

    def ingest_observation(self, observation: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._service().ingest_observation(observation)
        except Exception as error:
            if _exception_named(error, "ObservationConflictError"):
                raise ObservationConflict(str(error)) from error
            raise
