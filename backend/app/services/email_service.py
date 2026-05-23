from __future__ import annotations

from email.message import EmailMessage
import smtplib

from backend.app.core.config import get_settings
from backend.app.storage.database import utc_now_iso


class EmailService:
    def build_alert(self, incident: dict) -> tuple[str, str, str]:
        plates = ", ".join(plate["plate_number"] for plate in incident.get("plates", [])) or "UNKNOWN"
        recipient = incident["police_station_email"]
        subject = f"Accident Alert - {incident['location_name']}"
        body = "\n".join(
            [
                "Automated road accident alert",
                "",
                f"Location: {incident['location_name']}",
                f"Coordinates: {incident['latitude']}, {incident['longitude']}",
                f"Detected at: {incident['detected_at']}",
                f"Accident confidence: {incident['accident_confidence']:.2f}",
                f"Detected number plates: {plates}",
                f"Evidence image: {incident['evidence_image']}",
                "",
                "Please review and dispatch officers if required.",
            ]
        )
        return recipient, subject, body

    def send_alert(self, incident: dict) -> dict:
        settings = get_settings()
        recipient, subject, body = self.build_alert(incident)
        if settings.email_mode == "smtp" and settings.smtp_host:
            return self._send_smtp(recipient, subject, body)
        return {
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "status": "sent_mock",
            "provider": "mock",
            "sent_at": utc_now_iso(),
            "error": None,
        }

    def _send_smtp(self, recipient: str, subject: str, body: str) -> dict:
        settings = get_settings()
        try:
            message = EmailMessage()
            message["From"] = settings.smtp_from
            message["To"] = recipient
            message["Subject"] = subject
            message.set_content(body)
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.starttls()
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
            return {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": "sent",
                "provider": "smtp",
                "sent_at": utc_now_iso(),
                "error": None,
            }
        except Exception as exc:
            return {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "status": "failed",
                "provider": "smtp",
                "sent_at": utc_now_iso(),
                "error": str(exc),
            }

