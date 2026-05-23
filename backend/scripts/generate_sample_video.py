from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PATH = ROOT / "samples" / "sample_accident.mp4"


def draw_car(frame, x, y, color, label):
    cv2.rectangle(frame, (x, y), (x + 180, y + 70), color, -1)
    cv2.circle(frame, (x + 35, y + 72), 18, (25, 25, 25), -1)
    cv2.circle(frame, (x + 145, y + 72), 18, (25, 25, 25), -1)
    cv2.rectangle(frame, (x + 58, y + 45), (x + 128, y + 68), (245, 245, 245), -1)
    cv2.putText(frame, label, (x + 62, y + 62), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (20, 20, 20), 1)


def main():
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    width, height = 960, 540
    writer = cv2.VideoWriter(
        str(SAMPLE_PATH),
        cv2.VideoWriter_fourcc(*"mp4v"),
        20,
        (width, height),
    )
    for frame_index in range(90):
        frame = np.full((height, width, 3), (210, 216, 218), dtype=np.uint8)
        cv2.rectangle(frame, (0, 290), (width, 450), (70, 76, 78), -1)
        cv2.line(frame, (0, 370), (width, 370), (230, 230, 230), 4)
        cv2.putText(frame, "CCTV-01 Baseline Road", (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (30, 45, 55), 2)

        left_x = 90 + frame_index * 4
        right_x = 690 - frame_index * 4
        if frame_index >= 52:
            left_x = 300
            right_x = 476
        draw_car(frame, left_x, 310, (64, 130, 220), "WP CAB-1234")
        draw_car(frame, right_x, 310, (72, 170, 92), "CP KE-7781")

        if frame_index >= 52:
            cv2.circle(frame, (472, 338), 72, (35, 35, 230), -1)
            cv2.putText(frame, "ACCIDENT", (392, 343), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
            cv2.line(frame, (430, 292), (515, 390), (255, 255, 255), 4)
            cv2.line(frame, (515, 292), (430, 390), (255, 255, 255), 4)

        writer.write(frame)
    writer.release()
    print(f"Created {SAMPLE_PATH}")


if __name__ == "__main__":
    main()

