import json

from fastapi.testclient import TestClient

from app.main import app
from app.services.risk_service_adapter import RiskServiceAdapter


def test_api_uses_m3_null_threshold_and_unmapped_assessments(tmp_path):
    roads_file = tmp_path / "roads.json"
    roads_file.write_text(
        json.dumps([
            {
                "road_id": "MAPPED-NULL",
                "road_name": "Mapped without threshold",
                "threshold_minutes": None,
                "severity": "UNKNOWN",
            },
            {
                "road_id": "UNMAPPED-NULL",
                "road_name": "Unmapped without threshold",
                "threshold_minutes": None,
                "severity": "UNKNOWN",
            },
        ]),
        encoding="utf-8",
    )
    adapter = RiskServiceAdapter.from_roads_file(
        roads_file_path=roads_file,
        road_to_location_json='{"MAPPED-NULL":"LOC-NULL"}',
    )
    previous = app.state.risk_service_adapter
    app.state.risk_service_adapter = adapter

    try:
        client = TestClient(app)

        no_data = client.get("/api/roads/MAPPED-NULL/risk").json()
        assert no_data["risk_level"] == "UNKNOWN"
        assert no_data["data_freshness"] == "NO_DATA"
        assert no_data["historical_threshold_minutes"] is None

        ingested = client.post(
            "/api/observations",
            json={
                "location_id": "LOC-NULL",
                "timestamp": "2026-10-09T10:00:00Z",
                "rainfall_intensity_mm_hr": 15.0,
                "is_raining": True,
            },
        )
        assert ingested.status_code == 200

        observed = client.get("/api/roads/MAPPED-NULL/risk?as_of=2026-10-09T10:05:00Z").json()
        assert observed["status"] == "threshold_unavailable"
        assert observed["risk_level"] == "UNKNOWN"
        assert observed["historical_threshold_minutes"] is None

        batch = client.get("/api/roads/risk?as_of=2026-10-09T10:05:00Z").json()
        single_unmapped = client.get(
            "/api/roads/UNMAPPED-NULL/risk?as_of=2026-10-09T10:05:00Z"
        ).json()
        batch_unmapped = next(
            road for road in batch["roads"] if road["road_id"] == "UNMAPPED-NULL"
        )
        assert single_unmapped == batch_unmapped
        assert single_unmapped["risk_level"] == "UNKNOWN"
        assert single_unmapped["data_freshness"] == "UNMAPPED"
        assert single_unmapped["historical_threshold_minutes"] is None
    finally:
        app.state.risk_service_adapter = previous
