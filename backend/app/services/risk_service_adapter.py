"""Thin adapter for M3's public ``WaterloggingRiskService`` facade.

This layer delegates risk calculations and observation ingestion to M3 and
normalizes service exceptions. It retains a compatibility fallback for older
M3 facades that raised on a single-road unmapped query; the current facade
returns the same UNKNOWN / UNMAPPED assessment in single and batch queries.
"""

from datetime import datetime
import json
from pathlib import Path
import sys
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

    @classmethod
    def from_roads_file(
        cls,
        roads_file_path: Path,
        road_to_location_json: str = "{}",
    ) -> "RiskServiceAdapter":
        """Load M3's facade from the configured root risk-engine package."""
        try:
            mapping = json.loads(road_to_location_json)
        except json.JSONDecodeError as error:
            raise ValueError("GARUDAROUTE_RISK_ROAD_TO_LOCATION_JSON must be a JSON object") from error
        if not isinstance(mapping, dict) or any(
            not isinstance(road_id, str)
            or not road_id.strip()
            or not isinstance(location_id, str)
            or not location_id.strip()
            for road_id, location_id in mapping.items()
        ):
            raise ValueError("Road-to-location mappings must be non-empty string pairs")
        mapping = {road_id.strip(): location_id.strip() for road_id, location_id in mapping.items()}

        repository_root = Path(__file__).resolve().parents[3]
        risk_engine_root = repository_root / "risk-engine"
        if str(risk_engine_root) not in sys.path:
            sys.path.insert(0, str(risk_engine_root))

        # M3 publishes this facade at risk-engine/engine/service.py. The folder
        # is added to sys.path because its current package imports are top-level.
        from engine.service import WaterloggingRiskService

        implementation = WaterloggingRiskService.from_roads_file(
            roads_file_path=roads_file_path,
            road_to_location=mapping,
        )
        return cls(implementation)

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
