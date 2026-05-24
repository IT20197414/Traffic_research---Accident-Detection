import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, Camera, Mail, MapPin, RefreshCw, Send, Upload } from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState("");
  const [video, setVideo] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [activeIncident, setActiveIncident] = useState(null);
  const [emailPreview, setEmailPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    const [profileResponse, incidentResponse] = await Promise.all([
      fetch(`${API_BASE}/api/camera-profiles`),
      fetch(`${API_BASE}/api/incidents`),
    ]);
    const profileData = await profileResponse.json();
    const incidentData = await incidentResponse.json();
    setProfiles(profileData);
    setSelectedProfile(String(profileData[0]?.id || ""));
    setIncidents(incidentData);
    setActiveIncident(incidentData[0] || null);
  }

  async function analyzeVideo(event) {
    event.preventDefault();
    if (!video || !selectedProfile) {
      setMessage("Choose a camera profile and upload a video first.");
      return;
    }
    setBusy(true);
    setMessage("Analyzing video frames...");
    const form = new FormData();
    form.append("camera_profile_id", selectedProfile);
    form.append("video", video);
    const response = await fetch(`${API_BASE}/api/incidents/analyze`, {
      method: "POST",
      body: form,
    });
    if (!response.ok) {
      const error = await response.json();
      setBusy(false);
      setMessage(error.detail || "Analysis failed.");
      return;
    }
    const incident = await response.json();
    setActiveIncident(incident);
    setIncidents((current) => [incident, ...current]);
    setEmailPreview(null);
    setMessage("Incident created. Evidence and plate data are ready.");
    setBusy(false);
  }

  async function sendEmail() {
    if (!activeIncident) return;
    setBusy(true);
    const response = await fetch(`${API_BASE}/api/incidents/${activeIncident.id}/send-email`, {
      method: "POST",
    });
    const log = await response.json();
    setEmailPreview(log);
    const updated = { ...activeIncident, email_status: log.status };
    setActiveIncident(updated);
    setIncidents((current) => current.map((incident) => (incident.id === updated.id ? updated : incident)));
    setMessage(`Email status: ${log.status}`);
    setBusy(false);
  }

  const selectedCamera = useMemo(
    () => profiles.find((profile) => String(profile.id) === selectedProfile),
    [profiles, selectedProfile],
  );

  return (
    <main className="shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Traffic Accident Monitoring System</p>
          <h1>Accident Alert Dashboard</h1>
        </div>
        <button className="iconButton" onClick={loadInitialData} title="Refresh incidents">
          <RefreshCw size={18} />
        </button>
      </section>

      <section className="workspace">
        <aside className="panel uploadPanel">
          <div className="panelTitle">
            <Upload size={18} />
            <h2>Analyze Video</h2>
          </div>
          <form onSubmit={analyzeVideo} className="stack">
            <label>
              Camera profile
              <select value={selectedProfile} onChange={(event) => setSelectedProfile(event.target.value)}>
                {profiles.map((profile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Accident video
              <input type="file" accept="video/*" onChange={(event) => setVideo(event.target.files?.[0] || null)} />
            </label>
            {selectedCamera && (
              <div className="cameraBox">
                <Camera size={18} />
                <span>{selectedCamera.location_name}</span>
              </div>
            )}
            <button className="primaryButton" disabled={busy}>
              <AlertTriangle size={18} />
              Analyze Incident
            </button>
          </form>
          <p className="status">{message}</p>
        </aside>

        <section className="panel incidentPanel">
          <div className="panelTitle">
            <AlertTriangle size={18} />
            <h2>Incident Evidence</h2>
          </div>
          {activeIncident ? (
            <IncidentDetail incident={activeIncident} onSendEmail={sendEmail} busy={busy} emailPreview={emailPreview} />
          ) : (
            <div className="emptyState">Upload the sample video to create the first incident.</div>
          )}
        </section>

        <aside className="panel historyPanel">
          <div className="panelTitle">
            <MapPin size={18} />
            <h2>History</h2>
          </div>
          <div className="historyList">
            {incidents.map((incident) => (
              <button
                key={incident.id}
                className={`historyItem ${activeIncident?.id === incident.id ? "active" : ""}`}
                onClick={() => {
                  setActiveIncident(incident);
                  setEmailPreview(null);
                }}
              >
                <strong>{incident.location_name}</strong>
                <span>{new Date(incident.detected_at).toLocaleString()}</span>
                <small>{Math.round(incident.accident_confidence * 100)}% confidence</small>
              </button>
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}

function IncidentDetail({ incident, onSendEmail, busy, emailPreview }) {
  return (
    <div className="incidentDetail">
      <div className="evidenceFrame">
        <img
          src={`${API_BASE}${incident.evidence_overlay_image || incident.evidence_image}`}
          alt="Accident evidence frame"
        />
      </div>
      <div className="metrics">
        <Metric label="Confidence" value={`${Math.round(incident.accident_confidence * 100)}%`} />
        <Metric label="Detection" value={incident.detection_source || "fallback"} />
        <Metric label="Model" value={incident.model_name || "fallback heuristic"} />
        <Metric
          label="Frame time"
          value={incident.accident_frame_second == null ? "not available" : `${incident.accident_frame_second}s`}
        />
        <Metric label="Email" value={incident.email_status.replace("_", " ")} />
        <Metric label="Police station" value={incident.police_station_name || "Assigned station"} />
      </div>
      <div className="infoGrid">
        <div>
          <span>Location</span>
          <strong>{incident.location_name}</strong>
        </div>
        <div>
          <span>Date and time</span>
          <strong>{new Date(incident.detected_at).toLocaleString()}</strong>
        </div>
        <div>
          <span>Coordinates</span>
          <strong>
            {incident.latitude}, {incident.longitude}
          </strong>
        </div>
      </div>
      <div className="plateGrid">
        {incident.plates.map((plate) => (
          <div className="plateCard" key={plate.id || plate.plate_number}>
            {plate.crop_image && <img src={`${API_BASE}${plate.crop_image}`} alt="Number plate crop" />}
            <strong>{plate.plate_number}</strong>
            <span>{Math.round(plate.plate_confidence * 100)}% OCR confidence</span>
          </div>
        ))}
      </div>
      <button className="primaryButton sendButton" onClick={onSendEmail} disabled={busy}>
        <Send size={18} />
        Send Police Alert
      </button>
      {emailPreview && (
        <div className="emailPreview">
          <div className="panelTitle">
            <Mail size={18} />
            <h2>Email Preview</h2>
          </div>
          <strong>{emailPreview.subject}</strong>
          <span>To: {emailPreview.recipient}</span>
          <pre>{emailPreview.body}</pre>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
