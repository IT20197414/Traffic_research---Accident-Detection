from pathlib import Path

from backend.scripts.validate_accident_dataset import validate_dataset


def test_validate_dataset_accepts_clean_yolo_layout(tmp_path: Path):
    root = tmp_path / "accident_detection"
    for split in ("train", "val"):
        image_dir = root / "images" / split
        label_dir = root / "labels" / split
        image_dir.mkdir(parents=True)
        label_dir.mkdir(parents=True)
        (image_dir / f"{split}_frame.jpg").write_bytes(b"fake-image")
        (label_dir / f"{split}_frame.txt").write_text("1 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    (root / "data.yaml").write_text('nc: 2\nnames: ["car", "accident"]\n', encoding="utf-8")

    result = validate_dataset(root)

    assert result.ok
    assert result.image_count == 2
    assert result.label_count == 2
    assert result.class_ids == {1}


def test_validate_dataset_rejects_invalid_class_id(tmp_path: Path):
    root = tmp_path / "accident_detection"
    image_dir = root / "images" / "train"
    label_dir = root / "labels" / "train"
    image_dir.mkdir(parents=True)
    label_dir.mkdir(parents=True)
    (root / "images" / "val").mkdir(parents=True)
    (root / "labels" / "val").mkdir(parents=True)
    (image_dir / "frame.jpg").write_bytes(b"fake-image")
    (label_dir / "frame.txt").write_text("2 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    (root / "data.yaml").write_text('nc: 2\nnames: ["car", "accident"]\n', encoding="utf-8")

    result = validate_dataset(root)

    assert not result.ok
    assert "Unexpected class IDs: [2]" in result.errors

