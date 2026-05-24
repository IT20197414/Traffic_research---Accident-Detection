from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
EXPECTED_CLASSES = {0, 1}


@dataclass
class DatasetValidationResult:
    image_count: int
    label_count: int
    class_ids: set[int]
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_dataset(dataset_root: Path) -> DatasetValidationResult:
    errors: list[str] = []
    class_ids: set[int] = set()
    image_count = 0
    label_count = 0

    data_yaml = dataset_root / "data.yaml"
    if not data_yaml.exists():
        errors.append("Missing data.yaml")

    for split in ("train", "val"):
        image_dir = dataset_root / "images" / split
        label_dir = dataset_root / "labels" / split
        if not image_dir.exists():
            errors.append(f"Missing image directory: {image_dir}")
            continue
        if not label_dir.exists():
            errors.append(f"Missing label directory: {label_dir}")
            continue

        images = sorted(path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
        image_count += len(images)
        for image_path in images:
            label_path = label_dir / f"{image_path.stem}.txt"
            if not label_path.exists():
                errors.append(f"Missing label for {image_path.name} in {split}")
                continue
            label_count += 1
            _validate_label_file(label_path, class_ids, errors)

    invalid_classes = class_ids - EXPECTED_CLASSES
    if invalid_classes:
        errors.append(f"Unexpected class IDs: {sorted(invalid_classes)}")

    return DatasetValidationResult(
        image_count=image_count,
        label_count=label_count,
        class_ids=class_ids,
        errors=errors,
    )


def _validate_label_file(label_path: Path, class_ids: set[int], errors: list[str]) -> None:
    for line_number, line in enumerate(label_path.read_text(errors="ignore").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 5:
            errors.append(f"{label_path.name}:{line_number} must contain 5 values")
            continue
        try:
            class_id = int(float(parts[0]))
            coordinates = [float(value) for value in parts[1:]]
        except ValueError:
            errors.append(f"{label_path.name}:{line_number} contains non-numeric values")
            continue
        class_ids.add(class_id)
        if any(value < 0 or value > 1 for value in coordinates):
            errors.append(f"{label_path.name}:{line_number} has YOLO coordinates outside 0..1")
        if coordinates[2] <= 0 or coordinates[3] <= 0:
            errors.append(f"{label_path.name}:{line_number} has non-positive box size")


def main() -> None:
    dataset_root = Path("datasets/accident_detection")
    result = validate_dataset(dataset_root)
    print(f"Images: {result.image_count}")
    print(f"Labels: {result.label_count}")
    print(f"Class IDs: {sorted(result.class_ids)}")
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Dataset validation passed")


if __name__ == "__main__":
    main()

