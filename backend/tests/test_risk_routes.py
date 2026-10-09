import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.risk_service_adapter import RiskServiceAdapter


class RoadNotFoundError(Exception):
    pass


class RoadMappingNotFoundError(Exception):
    pass


class ObservationConflictError(Exception):
    pass


UNMAPPED = {
    "status": "error",
    "road_id": "ROAD-UNMAPPED",
    "road_name": "Unmapped Road",
    "location_id": None,
    "current_duration_minutes": 0.0,
    "historical_threshold_minutes": None,
    "risk_level": "UNKNOWN",
    "severity": None,
    "is_raining": False,
    "data_freshness": "UNMAPPED",
    "last_observation_timestamp": None,
    "reason": "No explicit road-to-location mapping.",
    "evaluated_at": "2026-10-09T00:00:00+00:00",
}


class FakeM3Service:
    def __init__(self) -> None:
        self.observations: list[dict] = []
        self.mapped = {
            **UNMAPPED,
            "status": "success",
            "road_id": "ROAD-MAPPED",
            "road_name": "Mapped Road",
            "location_id": "LOC-1",
            "data_freshness": "NO_DATA",
            "reason": "No observation available.",
        }

    def get_all_roads_risk(self, as_of=None):
        return [self.mapped, UNMAPPED]

    def get_road_risk(self, road_id: str, as_of=None):
        if road_id == "ROAD-UNMAPPED":
            raise RoadMappingNotFoundError(road_id)
        if road_id != "ROAD-MAPPED":
            raise RoadNotFoundError(road_id)
        return self.mapped

    def ingest_observation(self, observation: dict):
        if self.observations and observation["timestamp"] == self.observations[-1]["timestamp"]:
            raise ObservationConflictError("conflicting observation")
        self.observations.append(observation)
        return {"status": "ingested", "location_id": observation["location_id"]}


@pytest.fixture
def client():
    previous = app.state.risk_service_adapter
    app.state.risk_service_adapter = RiskServiceAdapter(FakeM3Service())
    try:
        yield TestClient(app)
    finally:
        app.state.risk_service_adapter = previous


def test_collection_returns_envelope_and_preserves_unknown_no_data(client):
    response = client.get("/api/roads/risk")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert [road["risk_level"] for road in payload["roads"]] == ["UNKNOWN", "UNKNOWN"]
    assert payload["roads"][0]["data_freshness"] == "NO_DATA"


def test_known_unmapped_single_matches_collection_assessment(client):
    batch = client.get("/api/roads/risk").json()["roads"][1]
    single = client.get("/api/roads/ROAD-UNMAPPED/risk").json()

    assert single == batch


def test_unknown_road_returns_404(client):
    assert client.get("/api/roads/MISSING/risk").status_code == 404


def test_invalid_as_of_returns_422(client):
    assert client.get("/api/roads/risk?as_of=not-a-date").status_code == 422
    assert client.get("/api/roads/risk?as_of=2026-10-09T10:00:00").status_code == 422


def test_observation_is_accepted_and_conflict_returns_409(client):
    payload = {
        "location_id": "LOC-1",
        "timestamp": "2026-10-09T10:00:00Z",
        "rainfall_intensity_mm_hr": 4.5,
    }
    assert client.post("/api/observations", json=payload).status_code == 200
    conflict = client.post("/api/observations", json={**payload, "rainfall_intensity_mm_hr": 8})
    assert conflict.status_code == 409


def test_invalid_observation_payload_returns_422(client):
    response = client.post(
        "/api/observations",
        json={
            "location_id": "LOC-1",
            "timestamp": "2026-10-09T10:00:00",
            "rainfall_intensity_mm_hr": -1,
        },
    )
    assert response.status_code == 422


def test_unconfigured_service_returns_503():
    previous = app.state.risk_service_adapter
    app.state.risk_service_adapter = RiskServiceAdapter()
    try:
        assert TestClient(app).get("/api/roads/risk").status_code == 503
    finally:
        app.state.risk_service_adapter = previous
