# Road Accident Detection and Alert System

A computer vision based traffic monitoring system that detects road accident events from video footage, stores incident evidence, extracts visible vehicle plate information, and sends automated email alerts to the nearest police station.

This project was developed as part of a final year research project and demonstrates an end-to-end accident reporting workflow using video analysis, backend APIs, local persistence, a web dashboard, and SMTP-based alerting.

## Features

- Upload and analyze traffic video footage.
- Detect accident evidence frames using OpenCV and an optional YOLO model.
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
samples/          Sample traffic video for local testing
media/            Runtime storage for uploads, evidence images, and plate crops
requirements.txt  Python dependencies
```

## Setup

```powershell
cd D:\Projects\Traffic_Project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install --prefix frontend
python backend\scripts\generate_sample_video.py
```

## Run The Application

Start the backend:

```powershell
cd D:\Projects\Traffic_Project
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
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

By default, the system uses mock email mode so the alert workflow can be tested without real SMTP credentials.

To send real emails, configure SMTP environment variables before starting the backend:

```powershell
$env:EMAIL_MODE="smtp"
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your-sender-email@gmail.com"
$env:SMTP_PASSWORD="your-gmail-app-password"
$env:SMTP_FROM="your-sender-email@gmail.com"

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Do not commit real email passwords or app passwords to the repository.

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
