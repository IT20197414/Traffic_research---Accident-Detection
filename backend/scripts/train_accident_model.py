from __future__ import annotations

from pathlib import Path
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.validate_accident_dataset import validate_dataset

DATASET_ROOT = PROJECT_ROOT / "datasets" / "accident_detection"
MODEL_TARGET = PROJECT_ROOT / "backend" / "models" / "accident_yolov8.pt"


def main() -> None:
    result = validate_dataset(DATASET_ROOT)
    if not result.ok:
        for error in result.errors:
            print(error)
        raise SystemExit(1)

    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")
    train_result = model.train(
        data=str(DATASET_ROOT / "data.yaml"),
        epochs=10,
        imgsz=640,
        batch=8,
        patience=5,
        project=str(PROJECT_ROOT / "runs" / "accident_detection"),
        name="yolov8n_accident",
        exist_ok=True,
    )
    best_model = Path(train_result.save_dir) / "weights" / "best.pt"
    MODEL_TARGET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_model, MODEL_TARGET)
    print(f"Saved trained model to {MODEL_TARGET}")


if __name__ == "__main__":
    main()
