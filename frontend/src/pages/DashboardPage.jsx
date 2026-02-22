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
  const [chatHistory, setChatHistory] = useState([]);
  const [practiceRows, setPracticeRows] = useState([]);
  const [downloadError, setDownloadError] = useState("");

  useEffect(() => {
    api.get("/style/mine").then((res) => {
      if (!res.data.learning_style) {
        navigate("/style");
        return;
      }
      setStyleData(res.data);
    });

    Promise.allSettled([
      api.get("/downloads/mine"),
      api.get("/chat/history"),
      api.get("/practice/mine"),
    ]).then(([d, c, p]) => {
      if (d.status === "fulfilled") setDownloads(d.value.data || []);
      if (c.status === "fulfilled") setChatHistory(c.value.data || []);
      if (p.status === "fulfilled") setPracticeRows(p.value.data || []);
    });
  }, [navigate]);

  const label = styleData?.learning_style
    ? styleData.learning_style.charAt(0).toUpperCase() + styleData.learning_style.slice(1)
    : "Not set";

  const completedCount = practiceRows.filter((r) => r.status === "completed").length;
  const totalPracticeTime = practiceRows.reduce((sum, r) => sum + (r.time_spent || 0), 0);
  const latestQuestion = chatHistory[0]?.question || "Ask your first question to start.";
  const recommendedAction =
    styleData?.learning_style === "kinesthetic"
      ? "Open practice lab and complete one guided task."
      : "Ask chatbot for one concept and download the personalized resource.";

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
      <div className="container page-wrap">
        <header className="page-header">
          <p className="page-kicker mb-1">Personalized Command Center</p>
          <h2 className="page-title">Welcome back, {user?.name}</h2>
          <p className="page-subtitle">Track your adaptive learning progress and continue from where you stopped.</p>
        </header>

        <div className="glass-card p-4 mb-4">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
            <div>
              <p className="mb-1">Detected Learning Style: <span className="badge badge-soft">{label}</span></p>
              {styleData && (
                <p className="mb-0 text-muted">
                  V: {styleData.visual_score} | A: {styleData.auditory_score} | K: {styleData.kinesthetic_score}
                </p>
              )}
            </div>
            <div className="d-flex gap-2 flex-wrap">
              <Link to="/chat" className="btn brand-btn">Ask AI Chatbot</Link>
              {styleData?.learning_style === "kinesthetic" && (
                <Link to="/practice" className="btn btn-warning">Open Practice Lab</Link>
              )}
              <Link to="/style" className="btn surface-btn">Retake Style Test</Link>
            </div>
          </div>

          <div className="metric-grid">
            <article className="metric-card">
              <p className="metric-label">Questions Asked</p>
              <div className="metric-value">{chatHistory.length}</div>
              <p className="metric-foot">Conversation history saved</p>
            </article>
            <article className="metric-card">
              <p className="metric-label">Total Downloads</p>
              <div className="metric-value">{downloads.length}</div>
              <p className="metric-foot">Resources generated for you</p>
            </article>
            <article className="metric-card">
              <p className="metric-label">Practice Completed</p>
              <div className="metric-value">{completedCount}</div>
              <p className="metric-foot">Hands-on tasks finished</p>
            </article>
            <article className="metric-card">
              <p className="metric-label">Practice Time</p>
              <div className="metric-value">{totalPracticeTime}s</div>
              <p className="metric-foot">Tracked coding duration</p>
            </article>
          </div>
        </div>

        <div className="row g-3 mb-4">
          <div className="col-lg-6">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-2">Latest Learning Context</h5>
              <p className="mb-2 text-muted"><strong>Last asked:</strong> {latestQuestion}</p>
              <p className="mb-0"><strong>Recommended next step:</strong> {recommendedAction}</p>
            </div>
          </div>
          <div className="col-lg-6">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-2">Quick Actions</h5>
              <div className="d-grid gap-2">
                <Link to="/chat" className="btn surface-btn text-start">Continue AI conversation</Link>
                <Link to="/practice" className="btn surface-btn text-start">Continue virtual practice</Link>
                <Link to="/style" className="btn surface-btn text-start">Retake learning style assessment</Link>
              </div>
            </div>
          </div>
        </div>

        <div className="glass-card p-4">
          <h5 className="mb-3">Download History</h5>
          {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}
          {downloads.length === 0 ? (
            <p className="text-muted mb-0">No downloads yet.</p>
          ) : (
            <ul className="mb-0 list-unstyled d-grid gap-2">
              {downloads.map((d) => (
                <li key={d.download_id} className="soft-card p-2 d-flex justify-content-between align-items-center">
                  <span><strong>{d.content_type}</strong> | {new Date(d.timestamp).toLocaleString()}</span>
                  <button className="btn btn-sm surface-btn" onClick={() => downloadHistoryFile(d)}>
                    Download
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
