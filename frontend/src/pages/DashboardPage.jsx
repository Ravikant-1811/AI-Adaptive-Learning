import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import { useAuth } from "../contexts/AuthContext";
import api from "../services/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [styleData, setStyleData] = useState(null);
  const [downloads, setDownloads] = useState([]);

  useEffect(() => {
    api.get("/style/mine").then((res) => {
      if (!res.data.learning_style) {
        navigate("/style");
        return;
      }
      setStyleData(res.data);
    });

    api.get("/downloads/mine").then((res) => setDownloads(res.data));
  }, [navigate]);

  const label = styleData?.learning_style
    ? styleData.learning_style.charAt(0).toUpperCase() + styleData.learning_style.slice(1)
    : "Not set";

  return (
    <>
      <NavBar />
      <div className="container pb-5">
        <div className="glass-card p-4 mb-4">
          <h3>Welcome, {user?.name}</h3>
          <p className="mb-1">Detected Learning Style: <strong>{label}</strong></p>
          {styleData && (
            <p className="mb-0 text-muted">
              Scores | Visual: {styleData.visual_score} | Auditory: {styleData.auditory_score} | Kinesthetic: {styleData.kinesthetic_score}
            </p>
          )}
          <div className="d-flex flex-wrap gap-2 mt-3">
            <Link to="/chat" className="btn btn-primary">Ask AI Chatbot</Link>
            {styleData?.learning_style === "kinesthetic" && (
              <Link to="/practice" className="btn btn-warning">Open Virtual Practice Lab</Link>
            )}
            <Link to="/style" className="btn btn-outline-secondary">Retake/Change Learning Style</Link>
          </div>
        </div>

        <div className="glass-card p-4">
          <h5>Download History</h5>
          {downloads.length === 0 ? (
            <p className="text-muted mb-0">No downloads yet.</p>
          ) : (
            <ul className="mb-0">
              {downloads.map((d) => (
                <li key={d.download_id}>
                  {d.content_type} | 
                  <a
                    href={`${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api"}${d.download_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="ms-1"
                  >
                    Download file
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
