from pydantic import BaseModel


class CameraProfile(BaseModel):
    id: int
    name: str
    location_name: str
    latitude: float
    longitude: float
    police_station_name: str
    police_station_email: str


class DetectedPlate(BaseModel):
    id: int | None = None
    incident_id: str | None = None
    plate_number: str
    plate_confidence: float
    crop_image: str | None = None
    vehicle_confidence: float


class Incident(BaseModel):
    id: str
    camera_profile_id: int
    camera_name: str | None = None
    location_name: str
    latitude: float
    longitude: float
    detected_at: str
    accident_confidence: float
    evidence_image: str
    uploaded_video: str
    email_status: str
    police_station_name: str | None = None
    police_station_email: str | None = None
    plates: list[DetectedPlate] = []


class EmailLog(BaseModel):
    id: int
    incident_id: str
    recipient: str
    subject: str
    body: str
    status: str
    provider: str
    sent_at: str
    error: str | None = None

