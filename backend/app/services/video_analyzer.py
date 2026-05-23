from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np

from backend.app.core.config import get_settings
from backend.app.services.plate_reader import PlateReader
from backend.app.storage.database import utc_now_iso


class VideoAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.plate_reader = PlateReader()
        self._yolo_model = None

    def analyze(self, video_path: Path, camera_profile: dict[str, Any], source_label: str | None = None) -> dict[str, Any]:
        incident_id = str(uuid4())
        best_frame, confidence = self._find_best_accident_frame(video_path)
        evidence_name = f"{incident_id}_evidence.jpg"
        evidence_path = self.settings.evidence_dir / evidence_name
        cv2.imwrite(str(evidence_path), best_frame)

        plates = self.plate_reader.detect_and_read(best_frame, source_label or video_path.name, incident_id)
        incident = {
            "id": incident_id,
            "camera_profile_id": camera_profile["id"],
            "location_name": camera_profile["location_name"],
            "latitude": camera_profile["latitude"],
            "longitude": camera_profile["longitude"],
            "detected_at": utc_now_iso(),
            "accident_confidence": confidence,
            "evidence_image": f"/media/evidence/{evidence_name}",
            "uploaded_video": f"/media/uploads/{video_path.name}",
            "email_status": "not_sent",
        }
        vehicles = [{**plate, "incident_id": incident_id} for plate in plates]
        return {"incident": incident, "vehicles": vehicles}

    def _find_best_accident_frame(self, video_path: Path):
        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise ValueError("Could not open uploaded video")

        best_frame = None
        best_confidence = 0.0
        frame_index = 0

        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index += 1
            if frame_index % 5 != 0:
                continue
            confidence = max(
                self._red_impact_confidence(frame),
                self._yolo_accident_confidence(frame),
            )
            if confidence > best_confidence or best_frame is None:
                best_confidence = confidence
                best_frame = frame.copy()

        capture.release()
        if best_frame is None:
            raise ValueError("Uploaded video did not contain readable frames")

        return best_frame, round(max(best_confidence, 0.35), 3)

    def _red_impact_confidence(self, frame) -> float:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red_1 = np.array([0, 70, 90])
        upper_red_1 = np.array([10, 255, 255])
        lower_red_2 = np.array([170, 70, 90])
        upper_red_2 = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_red_1, upper_red_1) | cv2.inRange(hsv, lower_red_2, upper_red_2)
        ratio = float(cv2.countNonZero(mask)) / float(frame.shape[0] * frame.shape[1])
        return min(0.99, ratio * 18)

    def _yolo_accident_confidence(self, frame) -> float:
        model = self._load_yolo_model()
        if model is None:
            return 0.0
        try:
            results = model.predict(frame, verbose=False, conf=0.25)
            boxes = results[0].boxes
            if boxes is None or boxes.conf is None:
                return 0.0
            names = getattr(results[0], "names", {})
            confidences = []
            for cls_id, conf in zip(boxes.cls.tolist(), boxes.conf.tolist()):
                label = str(names.get(int(cls_id), "")).lower()
                if "accident" in label or "crash" in label:
                    confidences.append(float(conf))
            return max(confidences, default=0.0)
        except Exception:
            return 0.0

    def _load_yolo_model(self):
        if self._yolo_model is not None:
            return self._yolo_model
        model_path = self.settings.accident_model_path
        if not model_path or not Path(model_path).exists():
            return None
        try:
            from ultralytics import YOLO

            self._yolo_model = YOLO(model_path)
            return self._yolo_model
        except Exception:
            return None
