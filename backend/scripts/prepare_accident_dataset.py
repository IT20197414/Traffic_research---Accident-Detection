from __future__ import annotations

from pathlib import Path
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.validate_accident_dataset import validate_dataset

SOURCE_ROOT = Path(
    r"D:\Projects\yolov8-vehicle-crash-detection-main\yolov8-vehicle-crash-detection-main\freedomtech"
)
TARGET_ROOT = PROJECT_ROOT / "datasets" / "accident_detection"


def copy_split(source_split: str, target_split: str) -> None:
    source_images = SOURCE_ROOT / "images" / source_split
    source_labels = SOURCE_ROOT / "labels" / source_split
    target_images = TARGET_ROOT / "images" / target_split
    target_labels = TARGET_ROOT / "labels" / target_split
    target_images.mkdir(parents=True, exist_ok=True)
    target_labels.mkdir(parents=True, exist_ok=True)

    for image_path in sorted(source_images.glob("*.jpg")):
        label_path = source_labels / f"{image_path.stem}.txt"
        if not label_path.exists():
            continue
        shutil.copy2(image_path, target_images / image_path.name)
        shutil.copy2(label_path, target_labels / label_path.name)


def write_data_yaml() -> None:
    data_yaml = TARGET_ROOT / "data.yaml"
    data_yaml.write_text(
        "\n".join(
            [
                f"path: {TARGET_ROOT.as_posix()}",
                "train: images/train",
                "val: images/val",
                "nc: 2",
                "names: [\"car\", \"accident\"]",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise SystemExit(f"Source dataset not found: {SOURCE_ROOT}")
    if TARGET_ROOT.exists():
        shutil.rmtree(TARGET_ROOT)
    copy_split("training", "train")
    copy_split("validation", "val")
    write_data_yaml()
    result = validate_dataset(TARGET_ROOT)
    if not result.ok:
        for error in result.errors:
            print(error)
        raise SystemExit(1)
    print(f"Prepared dataset at {TARGET_ROOT}")
    print(f"Images: {result.image_count}")
    print(f"Labels: {result.label_count}")
    print(f"Class IDs: {sorted(result.class_ids)}")


if __name__ == "__main__":
    main()
