from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np

from backend.app.core.config import get_settings
from backend.app.services.plate_reader import PlateReader
from backend.app.storage.database import utc_now_iso


@dataclass
class AccidentCandidate:
    frame: Any
    confidence: float
    frame_index: int
    frame_second: float
    detection_source: str
    model_name: str | None
    boxes: list[tuple[int, int, int, int, float]]


class VideoAnalyzer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.plate_reader = PlateReader()
        self._yolo_model = None

    def analyze(self, video_path: Path, camera_profile: dict[str, Any], source_label: str | None = None) -> dict[str, Any]:
        incident_id = str(uuid4())
        candidate = self._find_best_accident_frame(video_path)
        evidence_name = f"{incident_id}_evidence.jpg"
        overlay_name = f"{incident_id}_evidence_overlay.jpg"
        evidence_path = self.settings.evidence_dir / evidence_name
        overlay_path = self.settings.evidence_dir / overlay_name
        cv2.imwrite(str(evidence_path), candidate.frame)
        cv2.imwrite(str(overlay_path), self._annotate_frame(candidate))

        plates = self.plate_reader.detect_and_read(candidate.frame, source_label or video_path.name, incident_id)
        incident = {
            "id": incident_id,
            "camera_profile_id": camera_profile["id"],
            "location_name": camera_profile["location_name"],
            "latitude": camera_profile["latitude"],
            "longitude": camera_profile["longitude"],
            "detected_at": utc_now_iso(),
            "accident_confidence": round(candidate.confidence, 3),
            "evidence_image": f"/media/evidence/{evidence_name}",
            "detection_source": candidate.detection_source,
            "model_name": candidate.model_name,
            "accident_frame_second": round(candidate.frame_second, 2),
            "evidence_overlay_image": f"/media/evidence/{overlay_name}",
            "uploaded_video": f"/media/uploads/{video_path.name}",
            "email_status": "not_sent",
        }
        vehicles = [{**plate, "incident_id": incident_id} for plate in plates]
        return {"incident": incident, "vehicles": vehicles}

    def _find_best_accident_frame(self, video_path: Path) -> AccidentCandidate:
        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise ValueError("Could not open uploaded video")

        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        best_yolo: AccidentCandidate | None = None
        best_fallback: AccidentCandidate | None = None
        frame_index = 0

        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index += 1
            if frame_index % 5 != 0:
                continue
            frame_second = frame_index / fps
            yolo_candidate = self._yolo_accident_candidate(frame, frame_index, frame_second)
            if yolo_candidate and (best_yolo is None or yolo_candidate.confidence > best_yolo.confidence):
                best_yolo = yolo_candidate

            if self.settings.accident_fallback_enabled:
                fallback_confidence = self._red_impact_confidence(frame)
                if fallback_confidence > 0 and (
                    best_fallback is None or fallback_confidence > best_fallback.confidence
                ):
                    best_fallback = AccidentCandidate(
                        frame=frame.copy(),
                        confidence=fallback_confidence,
                        frame_index=frame_index,
                        frame_second=frame_second,
                        detection_source="fallback",
                        model_name=None,
                        boxes=[],
                    )

        capture.release()
        if best_yolo:
            return best_yolo
        if best_fallback:
            best_fallback.confidence = max(best_fallback.confidence, 0.35)
            return best_fallback
        raise ValueError("No accident evidence found. Configure ACCIDENT_MODEL_PATH or enable fallback detection.")

    def _red_impact_confidence(self, frame) -> float:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_red_1 = np.array([0, 70, 90])
        upper_red_1 = np.array([10, 255, 255])
        lower_red_2 = np.array([170, 70, 90])
        upper_red_2 = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_red_1, upper_red_1) | cv2.inRange(hsv, lower_red_2, upper_red_2)
        ratio = float(cv2.countNonZero(mask)) / float(frame.shape[0] * frame.shape[1])
        return min(0.99, ratio * 18)

    def _yolo_accident_candidate(self, frame, frame_index: int, frame_second: float) -> AccidentCandidate | None:
        model = self._load_yolo_model()
        if model is None:
            return None
        try:
            results = model.predict(frame, verbose=False, conf=0.25)
            parsed = self._parse_yolo_accident_result(results[0])
            if not parsed:
                return None
            best_confidence = max(box[4] for box in parsed)
            return AccidentCandidate(
                frame=frame.copy(),
                confidence=best_confidence,
                frame_index=frame_index,
                frame_second=frame_second,
                detection_source="yolo",
                model_name=Path(self.settings.accident_model_path).name,
                boxes=parsed,
            )
        except Exception:
            return None

    @staticmethod
    def _parse_yolo_accident_result(result) -> list[tuple[int, int, int, int, float]]:
        boxes = getattr(result, "boxes", None)
        if boxes is None or getattr(boxes, "conf", None) is None:
            return []
        names = getattr(result, "names", {})
        parsed: list[tuple[int, int, int, int, float]] = []
        xyxy_values = boxes.xyxy.tolist()
        class_values = boxes.cls.tolist()
        confidence_values = boxes.conf.tolist()
        for xyxy, cls_id, confidence in zip(xyxy_values, class_values, confidence_values):
            label = str(names.get(int(cls_id), "")).lower()
            if label != "accident":
                continue
            x1, y1, x2, y2 = [int(value) for value in xyxy]
            parsed.append((x1, y1, x2, y2, float(confidence)))
        return parsed

    def _annotate_frame(self, candidate: AccidentCandidate):
        frame = candidate.frame.copy()
        if candidate.boxes:
            for x1, y1, x2, y2, confidence in candidate.boxes:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (35, 35, 230), 3)
                cv2.putText(
                    frame,
                    f"accident {confidence:.2f}",
                    (x1, max(24, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (35, 35, 230),
                    2,
                )
        else:
            cv2.putText(
                frame,
                f"fallback accident evidence {candidate.confidence:.2f}",
                (24, 42),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (35, 35, 230),
                2,
            )
        return frame

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
