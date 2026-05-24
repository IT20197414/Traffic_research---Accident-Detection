from functools import lru_cache
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings:
    app_name = "Accident Alert Demo"
    database_path = Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "traffic_alerts.db"))
    media_root = Path(os.getenv("MEDIA_ROOT", PROJECT_ROOT / "media"))
    uploads_dir = media_root / "uploads"
    evidence_dir = media_root / "evidence"
    plate_crops_dir = media_root / "plate_crops"
    accident_model_path = os.getenv("ACCIDENT_MODEL_PATH", "")
    accident_fallback_enabled = os.getenv("ACCIDENT_FALLBACK_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
    email_mode = os.getenv("EMAIL_MODE", "mock").lower()
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", "traffic-alerts@example.com")
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.evidence_dir.mkdir(parents=True, exist_ok=True)
    settings.plate_crops_dir.mkdir(parents=True, exist_ok=True)
    return settings
