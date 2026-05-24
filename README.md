# Road Accident Detection and Alert System

A computer vision based traffic monitoring system that detects road accident events from video footage, stores incident evidence, extracts visible vehicle plate information, and sends automated email alerts to the nearest police station.

This project was developed as part of a final year research project and demonstrates an end-to-end accident reporting workflow using video analysis, backend APIs, local persistence, a web dashboard, and SMTP-based alerting.

## Features

- Upload and analyze traffic video footage.
- Detect accident evidence frames using a trained YOLOv8 model, with an OpenCV fallback for local testing.
- Capture and store accident evidence images.
- Extract visible vehicle number plate information with confidence values.
- Store camera profiles, incident records, detected vehicles, and email logs in SQLite.
- Send automated alert emails to the police station mapped to the selected camera location.
- Review incidents, evidence images, plate results, location data, and email status through a React dashboard.

## Technology Stack

- **Backend:** Python, FastAPI
- **Computer Vision:** OpenCV, Ultralytics YOLO support
- **Frontend:** React, Vite
- **Database:** SQLite
- **Email:** SMTP with mock mode support
- **Testing:** Pytest, FastAPI TestClient

## System Workflow

1. A user uploads traffic video footage through the web dashboard.
2. The backend samples video frames and identifies the strongest accident evidence frame.
3. The system saves the evidence image and attempts to extract visible number plate data.
4. Incident details are stored with location, date, time, confidence score, and police station mapping.
5. The user can send an automated email alert to the mapped police station email address.
6. The dashboard displays incident history, evidence, detected plates, and email status.

## Project Structure

```text
backend/          FastAPI application, analysis services, database layer, tests
frontend/         React dashboard
backend/models/   Trained YOLO model location
samples/          Sample traffic video for local testing
media/            Runtime storage for uploads, evidence images, and plate crops
requirements.txt  Python dependencies
run_backend.ps1   Local backend startup script that loads .env
```

## Setup

```powershell
cd D:\Projects\Traffic_Project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install --prefix frontend
python backend\scripts\generate_sample_video.py
Copy-Item .env.example .env
```

Update `.env` with your local model path and email settings. Do not commit `.env`.

## Accident Detection Model

The application supports a trained YOLOv8 accident detector. A clean YOLO dataset can be prepared from the older accident dataset with:

```powershell
python backend\scripts\prepare_accident_dataset.py
python backend\scripts\validate_accident_dataset.py
```

Train a lightweight YOLOv8 model locally:

```powershell
python backend\scripts\train_accident_model.py
```

The trained model is saved to:

```text
backend\models\accident_yolov8.pt
```

The trained model file is included in `backend/models` for local testing. The generated training dataset and YOLO run outputs are ignored because they can be recreated with the scripts above.

Start the backend with the trained model enabled either by setting `ACCIDENT_MODEL_PATH` manually or by using `.env` with `run_backend.ps1`.

Manual environment variable:

```powershell
$env:ACCIDENT_MODEL_PATH="D:\Projects\Traffic_Project\backend\models\accident_yolov8.pt"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

The dashboard displays whether an incident was detected by YOLO or by fallback logic, along with model name, confidence score, frame timestamp, and annotated evidence image.

## Improving Model Accuracy

The first trained model is suitable for integration testing, but accuracy depends heavily on the amount and quality of labeled traffic footage. To improve the model, collect both accident and normal-traffic videos, extract candidate frames, label accident regions, and retrain.

Extract frames from a video or folder of videos:

```powershell
python backend\scripts\extract_video_frames.py --input "D:\path\to\traffic_video.mp4" --every-seconds 1
```

Extracted frames are written to:

```text
datasets\frame_candidates
```

Scan a video with the current trained model and save detections for review:

```powershell
python backend\scripts\scan_video_with_model.py --video "D:\path\to\traffic_video.mp4"
```

Detection reports and annotated snapshots are written to:

```text
datasets\video_scans
```

These generated folders are ignored by Git because they are local data-preparation artifacts.

## Run The Application

Start the backend with the local `.env` file:

```powershell
cd D:\Projects\Traffic_Project
.\run_backend.ps1
```

Start the frontend:

```powershell
cd D:\Projects\Traffic_Project
npm run dev --prefix frontend
```

Open the dashboard:

```text
http://127.0.0.1:5173
```

## Email Configuration

By default, the system can use mock email mode so the alert workflow can be tested without real SMTP credentials.

For real emails, set these values in `.env`:

```text
EMAIL_MODE=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sender-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM=your-sender-email@gmail.com
```

Then start the backend:

```powershell
.\run_backend.ps1
```

Do not commit real email passwords or app passwords to the repository. `.env` is ignored by Git; `.env.example` is safe to commit because it only contains placeholders.

## Testing

Run backend tests:

```powershell
python -m pytest backend\tests
```

Build the frontend:

```powershell
npm run build --prefix frontend
```

## Future Improvements

- Train and integrate a dedicated YOLO accident detection model using real accident datasets.
- Improve number plate detection and OCR accuracy for low-quality CCTV footage.
- Add automatic nearest-police-station selection based on GPS coordinates.
- Add role-based authentication for police/admin users.
- Support live CCTV stream processing in addition to uploaded video files.
