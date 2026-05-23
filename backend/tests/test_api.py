from pathlib import Path
import os

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.storage.database import init_db


def test_analyze_sample_video_and_send_email():
    init_db()
    client = TestClient(app)
    sample = Path("samples/sample_accident.mp4")
    assert sample.exists(), "Run backend/scripts/generate_sample_video.py before API tests"

    with sample.open("rb") as video:
        response = client.post(
            "/api/incidents/analyze",
            data={"camera_profile_id": "1"},
            files={"video": ("sample_accident.mp4", video, "video/mp4")},
        )
    assert response.status_code == 200
    incident = response.json()
    assert incident["location_name"] == "Baseline Road, Colombo 08"
    assert incident["accident_confidence"] > 0.5
    assert incident["plates"][0]["plate_number"] == "WP CAB-1234"

    email_response = client.post(f"/api/incidents/{incident['id']}/send-email")
    assert email_response.status_code == 200
    assert email_response.json()["status"] == "sent_mock"

