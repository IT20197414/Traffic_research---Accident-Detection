from __future__ import annotations

import argparse
from pathlib import Path

import cv2


VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


def iter_videos(input_path: Path) -> list[Path]:
    if input_path.is_file() and input_path.suffix.lower() in VIDEO_EXTENSIONS:
        return [input_path]
    if input_path.is_dir():
        return sorted(path for path in input_path.rglob("*") if path.suffix.lower() in VIDEO_EXTENSIONS)
    raise ValueError(f"No supported video files found at {input_path}")


def extract_frames(video_path: Path, output_dir: Path, every_seconds: float, max_frames: int | None) -> int:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, int(round(fps * every_seconds)))
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    frame_index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if frame_index % step == 0:
            timestamp = frame_index / fps
            safe_stem = "".join(ch if ch.isalnum() else "_" for ch in video_path.stem)
            output_name = f"{safe_stem}_{timestamp:07.2f}s.jpg"
            cv2.imwrite(str(output_dir / output_name), frame)
            written += 1
            if max_frames and written >= max_frames:
                break
        frame_index += 1

    capture.release()
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract candidate training frames from traffic videos.")
    parser.add_argument("--input", required=True, help="Video file or directory containing videos.")
    parser.add_argument("--output", default="datasets/frame_candidates", help="Folder for extracted JPG frames.")
    parser.add_argument("--every-seconds", type=float, default=1.0, help="Extract one frame every N seconds.")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional max frames per video.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_root = Path(args.output)
    total = 0
    for video_path in iter_videos(input_path):
        video_output = output_root / video_path.stem
        count = extract_frames(video_path, video_output, args.every_seconds, args.max_frames)
        total += count
        print(f"{video_path}: {count} frames -> {video_output}")
    print(f"Total extracted frames: {total}")


if __name__ == "__main__":
    main()

