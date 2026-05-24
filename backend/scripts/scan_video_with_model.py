from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


def scan_video(video_path: Path, model_path: Path, output_dir: Path, confidence: float) -> Path:
    from ultralytics import YOLO

    output_dir.mkdir(parents=True, exist_ok=True)
    captures_dir = output_dir / "detections"
    captures_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{video_path.stem}_detections.csv"

    model = YOLO(str(model_path))
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    frame_index = 0
    rows: list[dict[str, object]] = []

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        frame_index += 1
        if frame_index % 5 != 0:
            continue
        results = model.predict(frame, verbose=False, conf=confidence)
        result = results[0]
        names = getattr(result, "names", {})
        boxes = getattr(result, "boxes", None)
        if boxes is None or getattr(boxes, "conf", None) is None:
            continue
        for xyxy, cls_id, conf in zip(boxes.xyxy.tolist(), boxes.cls.tolist(), boxes.conf.tolist()):
            label = str(names.get(int(cls_id), "")).lower()
            if label != "accident":
                continue
            second = frame_index / fps
            x1, y1, x2, y2 = [int(value) for value in xyxy]
            annotated = frame.copy()
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (35, 35, 230), 3)
            cv2.putText(
                annotated,
                f"accident {float(conf):.2f}",
                (x1, max(24, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (35, 35, 230),
                2,
            )
            image_name = f"{video_path.stem}_{second:07.2f}s_{float(conf):.2f}.jpg"
            cv2.imwrite(str(captures_dir / image_name), annotated)
            rows.append(
                {
                    "video": str(video_path),
                    "frame_index": frame_index,
                    "second": round(second, 2),
                    "confidence": round(float(conf), 4),
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "image": str(captures_dir / image_name),
                }
            )

    capture.release()

    with report_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["video", "frame_index", "second", "confidence", "x1", "y1", "x2", "y2", "image"],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Detections: {len(rows)}")
    print(f"Report: {report_path}")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan a video with the trained accident YOLO model.")
    parser.add_argument("--video", required=True, help="Video file to scan.")
    parser.add_argument(
        "--model",
        default="backend/models/accident_yolov8.pt",
        help="Path to trained accident YOLO model.",
    )
    parser.add_argument("--output", default="datasets/video_scans", help="Output folder for CSV and snapshots.")
    parser.add_argument("--confidence", type=float, default=0.25, help="YOLO confidence threshold.")
    args = parser.parse_args()

    scan_video(Path(args.video), Path(args.model), Path(args.output), args.confidence)


if __name__ == "__main__":
    main()

