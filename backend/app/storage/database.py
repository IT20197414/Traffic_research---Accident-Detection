from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import sqlite3
from typing import Any, Iterable

from backend.app.core.config import get_settings


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def dict_from_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def _connect() -> sqlite3.Connection:
    settings = get_settings()
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_connection() -> Iterable[sqlite3.Connection]:
    connection = _connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS camera_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                police_station_name TEXT NOT NULL,
                police_station_email TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                camera_profile_id INTEGER NOT NULL,
                location_name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                detected_at TEXT NOT NULL,
                accident_confidence REAL NOT NULL,
                evidence_image TEXT NOT NULL,
                uploaded_video TEXT NOT NULL,
                email_status TEXT NOT NULL DEFAULT 'not_sent',
                FOREIGN KEY (camera_profile_id) REFERENCES camera_profiles(id)
            );

            CREATE TABLE IF NOT EXISTS detected_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                plate_number TEXT NOT NULL,
                plate_confidence REAL NOT NULL,
                crop_image TEXT,
                vehicle_confidence REAL NOT NULL,
                FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL,
                provider TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                error TEXT,
                FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
            );
            """
        )

        count = connection.execute("SELECT COUNT(*) AS total FROM camera_profiles").fetchone()["total"]
        if count == 0:
            connection.executemany(
                """
                INSERT INTO camera_profiles
                    (name, location_name, latitude, longitude, police_station_name, police_station_email)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "CCTV-01 Baseline Road",
                        "Baseline Road, Colombo 08",
                        6.9147,
                        79.8791,
                        "Borella Police Station",
                        "borella.police@example.lk",
                    ),
                    (
                        "CCTV-02 Galle Road",
                        "Galle Road, Bambalapitiya",
                        6.8916,
                        79.8560,
                        "Bambalapitiya Police Station",
                        "bambalapitiya.police@example.lk",
                    ),
                    (
                        "CCTV-03 Kandy Road",
                        "Kandy Road, Kadawatha",
                        7.0030,
                        79.9504,
                        "Kadawatha Police Station",
                        "kadawatha.police@example.lk",
                    ),
                ],
            )

