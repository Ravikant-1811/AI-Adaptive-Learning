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
  const [insights, setInsights] = useState(null);
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
      api.get("/dashboard/insights"),
    ]).then(([d, c, p, i]) => {
      if (d.status === "fulfilled") setDownloads(d.value.data || []);
      if (c.status === "fulfilled") setChatHistory(c.value.data || []);
      if (p.status === "fulfilled") setPracticeRows(p.value.data || []);
      if (i.status === "fulfilled") setInsights(i.value.data || null);
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
  const recommendedTopic = insights?.recommended_topic || "Object-oriented programming fundamentals";
  const masteryScore = insights?.mastery_score ?? 0;
  const streakDays = insights?.streak_days ?? 0;

  const recommendationCards = [
    {
      key: "visual",
      title: "Visual",
      points: styleData?.visual_score || 0,
      tips: [
        "Use diagrams, charts, and mind maps for studying",
        "Color-code your notes and materials",
        "Watch educational videos and visual demonstrations",
      ],
    },
    {
      key: "auditory",
      title: "Auditory",
      points: styleData?.auditory_score || 0,
      tips: [
        "Listen to lectures and audio recordings",
        "Discuss topics with study groups",
        "Read your notes out loud",
      ],
    },
    {
      key: "kinesthetic",
      title: "Kinesthetic",
      points: styleData?.kinesthetic_score || 0,
      tips: [
        "Take frequent breaks to move around",
        "Use hands-on activities and experiments",
        "Act out concepts or use role-playing",
      ],
    },
  ];

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
            <article className="metric-card">
              <p className="metric-label">Mastery Score</p>
              <div className="metric-value">{masteryScore}</div>
              <p className="metric-foot">Calculated from learning activity</p>
            </article>
            <article className="metric-card">
              <p className="metric-label">Learning Streak</p>
              <div className="metric-value">{streakDays}d</div>
              <p className="metric-foot">Consecutive active days</p>
            </article>
          </div>
        </div>

        <div className="row g-3 mb-4">
          <div className="col-lg-6">
            <div className="glass-card p-4 h-100">
              <h5 className="mb-2">Latest Learning Context</h5>
              <p className="mb-2 text-muted"><strong>Last asked:</strong> {latestQuestion}</p>
              <p className="mb-0"><strong>Recommended next step:</strong> {recommendedAction}</p>
              <p className="mb-0 mt-2"><strong>AI Suggested Topic:</strong> {recommendedTopic}</p>
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

        {insights && (
          <div className="glass-card p-4 mb-4">
            <h5 className="mb-3">Activity Trends (Last 7 Days)</h5>
            <div className="row g-3">
              <div className="col-lg-4">
                <h6 className="mb-2">Chat Activity</h6>
                {(insights.daily_chat || []).map((d) => (
                  <div key={`c-${d.date}`} className="d-flex align-items-center gap-2 mb-1">
                    <small style={{ width: 80 }}>{d.date.slice(5)}</small>
                    <div className="progress flex-grow-1" style={{ height: 9 }}>
                      <div className="progress-bar" style={{ width: `${Math.min(100, d.count * 20)}%` }}></div>
                    </div>
                    <small>{d.count}</small>
                  </div>
                ))}
              </div>
              <div className="col-lg-4">
                <h6 className="mb-2">Practice Activity</h6>
                {(insights.daily_practice || []).map((d) => (
                  <div key={`p-${d.date}`} className="d-flex align-items-center gap-2 mb-1">
                    <small style={{ width: 80 }}>{d.date.slice(5)}</small>
                    <div className="progress flex-grow-1" style={{ height: 9 }}>
                      <div className="progress-bar bg-warning" style={{ width: `${Math.min(100, d.count * 20)}%` }}></div>
                    </div>
                    <small>{d.count}</small>
                  </div>
                ))}
              </div>
              <div className="col-lg-4">
                <h6 className="mb-2">Download Activity</h6>
                {(insights.daily_downloads || []).map((d) => (
                  <div key={`d-${d.date}`} className="d-flex align-items-center gap-2 mb-1">
                    <small style={{ width: 80 }}>{d.date.slice(5)}</small>
                    <div className="progress flex-grow-1" style={{ height: 9 }}>
                      <div className="progress-bar bg-success" style={{ width: `${Math.min(100, d.count * 20)}%` }}></div>
                    </div>
                    <small>{d.count}</small>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div className="glass-card p-4 mb-4">
          <h5 className="mb-3">Personalized Learning Recommendations</h5>
          <div className="recommend-grid">
            {recommendationCards.map((item) => (
              <article key={item.key} className={`recommend-card ${styleData?.learning_style === item.key ? "active" : ""}`}>
                <h6 className="mb-1">{item.title}</h6>
                <p className="text-muted mb-2">{item.points}/20 points</p>
                <ul className="mb-0 small">
                  {item.tips.map((tip) => (
                    <li key={tip}>{tip}</li>
                  ))}
                </ul>
              </article>
            ))}
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
