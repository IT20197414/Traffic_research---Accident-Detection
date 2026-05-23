from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.core.config import get_settings
from backend.app.schemas import CameraProfile, EmailLog, Incident
from backend.app.services.email_service import EmailService
from backend.app.services.video_analyzer import VideoAnalyzer
from backend.app.storage import repositories


router = APIRouter(prefix="/api", tags=["traffic-alerts"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/camera-profiles", response_model=list[CameraProfile])
def camera_profiles():
    return repositories.list_camera_profiles()


@router.post("/incidents/analyze", response_model=Incident)
async def analyze_incident(
    camera_profile_id: int = Form(...),
    video: UploadFile = File(...),
):
    profile = repositories.get_camera_profile(camera_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Camera profile not found")

    settings = get_settings()
    suffix = Path(video.filename or "upload.mp4").suffix or ".mp4"
    safe_name = f"{uuid4()}{suffix}"
    upload_path = settings.uploads_dir / safe_name
    with upload_path.open("wb") as output:
        while chunk := await video.read(1024 * 1024):
            output.write(chunk)

    try:
        analysis = VideoAnalyzer().analyze(upload_path, profile, video.filename)
        return repositories.create_incident(analysis["incident"], analysis["vehicles"])
    except ValueError as exc:
        upload_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/incidents", response_model=list[Incident])
def incidents():
    return repositories.list_incidents()


@router.get("/incidents/{incident_id}", response_model=Incident)
def incident_detail(incident_id: str):
    incident = repositories.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents/{incident_id}/send-email", response_model=EmailLog)
def send_email(incident_id: str):
    incident = repositories.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    log = EmailService().send_alert(incident)
    log["incident_id"] = incident_id
    created = repositories.create_email_log(log)
    repositories.update_email_status(incident_id, created["status"])
    return created


@router.get("/incidents/{incident_id}/email-logs", response_model=list[EmailLog])
def email_logs(incident_id: str):
    return repositories.list_email_logs(incident_id)
