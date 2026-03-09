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

  const learningMode = styleData?.learning_style
    ? styleData.learning_style.charAt(0).toUpperCase() + styleData.learning_style.slice(1)
    : "Not set";

  const completedCount = practiceRows.filter((r) => r.status === "completed").length;
  const totalPracticeTime = practiceRows.reduce((sum, r) => sum + (r.time_spent || 0), 0);
  const practiceMinutes = Math.round(totalPracticeTime / 60);
  const masteryScore = insights?.mastery_score ?? 0;
  const streakDays = insights?.streak_days ?? 0;

  const styleScores = [
    { key: "visual", name: "Visual", score: styleData?.visual_score || 0, cls: "s-visual" },
    { key: "auditory", name: "Auditory", score: styleData?.auditory_score || 0, cls: "s-auditory" },
    { key: "kinesthetic", name: "Kinesthetic", score: styleData?.kinesthetic_score || 0, cls: "s-kinesthetic" },
  ];

  const maxStyle = Math.max(...styleScores.map((s) => s.score), 1);

  const weeklyMax = Math.max(
    ...[...(insights?.daily_chat || []), ...(insights?.daily_practice || []), ...(insights?.daily_downloads || [])].map((x) => x.count || 0),
    1
  );

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

  const latestQuestion = chatHistory[0]?.question || "No question yet";
  const suggestedTopic = insights?.recommended_topic || "Object-oriented programming";

  return (
    <>
      <NavBar />
      <div className="container page-wrap dashboard-v2">
        <header className="db2-header">
          <div>
            <p className="db2-kicker mb-1">Learning Analytics</p>
            <h2 className="db2-title mb-1">Welcome, {user?.name}</h2>
            <p className="db2-subtitle mb-0">Mode: <strong>{learningMode}</strong></p>
          </div>
          <div className="d-flex gap-2 flex-wrap">
            <Link to="/chat" className="btn brand-btn">Open AI Chat</Link>
            <Link to="/practice" className="btn surface-btn">Practice Lab</Link>
          </div>
        </header>

        <section className="db2-kpis">
          <article className="db2-kpi">
            <p>Questions</p>
            <h3>{chatHistory.length}</h3>
            <span>AI conversations</span>
          </article>
          <article className="db2-kpi">
            <p>Downloads</p>
            <h3>{downloads.length}</h3>
            <span>Generated resources</span>
          </article>
          <article className="db2-kpi">
            <p>Practice</p>
            <h3>{completedCount}</h3>
            <span>Completed tasks</span>
          </article>
          <article className="db2-kpi">
            <p>Mastery</p>
            <h3>{masteryScore}%</h3>
            <span>Streak {streakDays} days</span>
          </article>
        </section>

        <section className="row g-3 mb-3">
          <div className="col-xl-6">
            <div className="db2-panel">
              <div className="db2-panel-head">
                <h5 className="mb-0">Learning Style Scores</h5>
                <small>/20 scale</small>
              </div>
              <div className="d-grid gap-3 mt-3">
                {styleScores.map((s) => (
                  <div key={s.key}>
                    <div className="d-flex justify-content-between mb-1">
                      <strong>{s.name}</strong>
                      <span>{s.score}</span>
                    </div>
                    <div className="db2-track">
                      <div className={`db2-fill ${s.cls}`} style={{ width: `${Math.max(8, Math.round((s.score / maxStyle) * 100))}%` }} />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <Link to="/style" className="btn btn-sm surface-btn">Retake Test</Link>
              </div>
            </div>
          </div>

          <div className="col-xl-6">
            <div className="db2-panel">
              <div className="db2-panel-head">
                <h5 className="mb-0">Weekly Activity</h5>
                <small>7 days</small>
              </div>
              <div className="db2-chart-row mt-3">
                <div className="db2-mini-chart">
                  <p className="db2-mini-title">Chat</p>
                  <div className="db2-bars">
                    {(insights?.daily_chat || []).map((d) => (
                      <div key={`c-${d.date}`} className="db2-bar-col">
                        <div className="db2-bar-bg">
                          <div className="db2-bar chat" style={{ height: `${Math.max(6, Math.round(((d.count || 0) / weeklyMax) * 100))}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="db2-mini-chart">
                  <p className="db2-mini-title">Practice</p>
                  <div className="db2-bars">
                    {(insights?.daily_practice || []).map((d) => (
                      <div key={`p-${d.date}`} className="db2-bar-col">
                        <div className="db2-bar-bg">
                          <div className="db2-bar practice" style={{ height: `${Math.max(6, Math.round(((d.count || 0) / weeklyMax) * 100))}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="db2-mini-chart">
                  <p className="db2-mini-title">Downloads</p>
                  <div className="db2-bars">
                    {(insights?.daily_downloads || []).map((d) => (
                      <div key={`d-${d.date}`} className="db2-bar-col">
                        <div className="db2-bar-bg">
                          <div className="db2-bar download" style={{ height: `${Math.max(6, Math.round(((d.count || 0) / weeklyMax) * 100))}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="row g-3 mb-3">
          <div className="col-xl-6">
            <div className="db2-panel h-100">
              <h5 className="mb-3">Current Learning Context</h5>
              <p><strong>Last Question:</strong> {latestQuestion}</p>
              <p><strong>Suggested Topic:</strong> {suggestedTopic}</p>
              <p><strong>Practice Time:</strong> {practiceMinutes} minutes</p>
            </div>
          </div>
          <div className="col-xl-6">
            <div className="db2-panel h-100">
              <h5 className="mb-3">Quick Actions</h5>
              <div className="d-grid gap-2">
                <Link to="/chat" className="btn surface-btn text-start">Ask detailed AI explanation</Link>
                <Link to="/practice" className="btn surface-btn text-start">Continue Java practice</Link>
                <Link to="/style" className="btn surface-btn text-start">Update learning style</Link>
              </div>
            </div>
          </div>
        </section>

        <section className="db2-panel">
          <h5 className="mb-3">Download History</h5>
          {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}
          {downloads.length === 0 ? (
            <p className="text-muted mb-0">No downloads yet.</p>
          ) : (
            <div className="db2-table-wrap">
              <table className="table table-sm mb-0">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Time</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {downloads.map((d) => (
                    <tr key={d.download_id}>
                      <td><span className="db2-pill">{d.content_type}</span></td>
                      <td>{new Date(d.timestamp).toLocaleString()}</td>
                      <td className="text-end">
                        <button className="btn btn-sm surface-btn" onClick={() => downloadHistoryFile(d)}>Download</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </>
  );
}
