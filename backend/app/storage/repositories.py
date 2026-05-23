from __future__ import annotations

from typing import Any

from backend.app.storage.database import dict_from_row, get_connection


def list_camera_profiles() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM camera_profiles ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def get_camera_profile(profile_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM camera_profiles WHERE id = ?", (profile_id,)).fetchone()
        return dict_from_row(row)


def create_incident(incident: dict[str, Any], vehicles: list[dict[str, Any]]) -> dict[str, Any]:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO incidents
                (id, camera_profile_id, location_name, latitude, longitude, detected_at,
                 accident_confidence, evidence_image, uploaded_video, email_status)
            VALUES
                (:id, :camera_profile_id, :location_name, :latitude, :longitude, :detected_at,
                 :accident_confidence, :evidence_image, :uploaded_video, :email_status)
            """,
            incident,
        )
        for vehicle in vehicles:
            connection.execute(
                """
                INSERT INTO detected_vehicles
                    (incident_id, plate_number, plate_confidence, crop_image, vehicle_confidence)
                VALUES
                    (:incident_id, :plate_number, :plate_confidence, :crop_image, :vehicle_confidence)
                """,
                vehicle,
            )
    created = get_incident(incident["id"])
    if not created:
        raise RuntimeError("Incident was not saved")
    return created


def list_incidents() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT i.*, c.name AS camera_name, c.police_station_name, c.police_station_email
            FROM incidents i
            JOIN camera_profiles c ON c.id = i.camera_profile_id
            ORDER BY i.detected_at DESC
            """
        ).fetchall()
        incidents = [dict(row) for row in rows]
    return [_with_plates(incident) for incident in incidents]


def get_incident(incident_id: str) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT i.*, c.name AS camera_name, c.police_station_name, c.police_station_email
            FROM incidents i
            JOIN camera_profiles c ON c.id = i.camera_profile_id
            WHERE i.id = ?
            """,
            (incident_id,),
        ).fetchone()
        incident = dict_from_row(row)
    return _with_plates(incident) if incident else None


def _with_plates(incident: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM detected_vehicles WHERE incident_id = ? ORDER BY id",
            (incident["id"],),
        ).fetchall()
        incident["plates"] = [dict(row) for row in rows]
    return incident


def update_email_status(incident_id: str, status: str) -> None:
    with get_connection() as connection:
        connection.execute("UPDATE incidents SET email_status = ? WHERE id = ?", (status, incident_id))


def create_email_log(log: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO email_logs
                (incident_id, recipient, subject, body, status, provider, sent_at, error)
            VALUES
                (:incident_id, :recipient, :subject, :body, :status, :provider, :sent_at, :error)
            """,
            log,
        )
        log_id = cursor.lastrowid
        row = connection.execute("SELECT * FROM email_logs WHERE id = ?", (log_id,)).fetchone()
        return dict(row)


def list_email_logs(incident_id: str) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM email_logs WHERE incident_id = ? ORDER BY sent_at DESC",
            (incident_id,),
        ).fetchall()
        return [dict(row) for row in rows]

