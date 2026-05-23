# Accident Alert Demo

An interview-ready rebuild of the accident alert module from the final-year research project.

The demo flow is:

1. Upload a CCTV/road video.
2. Analyze frames for an accident.
3. Save the best evidence frame.
4. Detect/read visible number plates with confidence values.
5. Store the incident in SQLite.
6. Generate a police-station email alert in mock mode, with optional SMTP sending.
7. Review everything in a React dashboard.

## Project Layout

```text
backend/          FastAPI app, SQLite storage, analysis and email services
frontend/         React dashboard
samples/          Demo videos generated locally
media/            Uploaded videos, evidence images, plate crops
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

## Run

Terminal 1:

```powershell
cd D:\Projects\Traffic_Project
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2:

```powershell
cd D:\Projects\Traffic_Project
npm run dev --prefix frontend
```

Open `http://localhost:5173`.

## Optional Real Email

Mock email is used by default. To use SMTP, set:

```powershell
$env:EMAIL_MODE="smtp"
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
$env:SMTP_FROM="traffic-alerts@example.com"
```

## Interview Explanation

The system is intentionally split into explainable layers:

- Computer vision pipeline: OpenCV reads frames and identifies the strongest accident evidence frame.
- Plate pipeline: plate candidates/OCR results are attached to the incident with confidence scores.
- Backend API: FastAPI exposes upload, history, detail, and send-email endpoints.
- Persistence: SQLite keeps camera profiles, incidents, detected vehicles, and email logs.
- Alerting: email service creates a police-station alert and uses mock or SMTP delivery.

