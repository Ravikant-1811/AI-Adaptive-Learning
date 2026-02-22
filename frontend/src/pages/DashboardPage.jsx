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
  const [downloadError, setDownloadError] = useState("");

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

  const downloadHistoryFile = async (item) => {
    setDownloadError("");
    try {
      const fileResp = await api.get(`/downloads/file/${item.download_id}`, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `download_${item.download_id}_${item.content_type}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.error || "Failed to download file.");
    }
  };

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
          {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}
          {downloads.length === 0 ? (
            <p className="text-muted mb-0">No downloads yet.</p>
          ) : (
            <ul className="mb-0">
              {downloads.map((d) => (
                <li key={d.download_id}>
                  {d.content_type} |
                  <button className="btn btn-link btn-sm p-0 ms-1 align-baseline" onClick={() => downloadHistoryFile(d)}>
                    Download file
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
