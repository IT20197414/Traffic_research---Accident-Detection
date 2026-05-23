from backend.app.services.email_service import EmailService
from backend.app.services.plate_reader import normalize_plate_text


def test_normalize_plate_text():
    assert normalize_plate_text(" wp cab-1234!! ") == "WP CAB-1234"
    assert normalize_plate_text("") == "UNKNOWN"


def test_mock_email_body_contains_incident_details():
    incident = {
        "location_name": "Baseline Road, Colombo 08",
        "latitude": 6.9147,
        "longitude": 79.8791,
        "detected_at": "2026-05-23T10:00:00+00:00",
        "accident_confidence": 0.94,
        "evidence_image": "/media/evidence/test.jpg",
        "police_station_email": "police@example.lk",
        "plates": [{"plate_number": "WP CAB-1234"}],
    }
    result = EmailService().send_alert(incident)
    assert result["status"] == "sent_mock"
    assert result["recipient"] == "police@example.lk"
    assert "WP CAB-1234" in result["body"]

