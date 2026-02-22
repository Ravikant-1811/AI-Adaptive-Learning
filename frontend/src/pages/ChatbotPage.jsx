import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

const QUICK_PROMPTS = [
  "Explain exception handling in Java",
  "What is polymorphism with example?",
  "Difference between interface and abstract class",
  "How does try-catch-finally work?",
];

function formatStyle(style) {
  if (!style) return "Unknown";
  return style.charAt(0).toUpperCase() + style.slice(1);
}

export default function ChatbotPage() {
  const navigate = useNavigate();
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [style, setStyle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadError, setDownloadError] = useState("");
  const [autoPack, setAutoPack] = useState([]);

  useEffect(() => {
    api.get("/style/mine").then((res) => setStyle(res.data.learning_style));
    api.get("/chat/history").then((res) => setHistory(res.data));
  }, []);

  const conversation = useMemo(() => {
    const rows = [...history].reverse();
    return rows.flatMap((h) => [
      {
        id: `q-${h.chat_id}`,
        role: "user",
        text: h.question,
        timestamp: h.timestamp,
      },
      {
        id: `a-${h.chat_id}`,
        role: "assistant",
        text: h.response,
        responseType: h.response_type,
        styleUsed: h.learning_style_used,
        sourceQuestion: h.question,
        timestamp: h.timestamp,
      },
    ]);
  }, [history]);

  const ask = async (prefill) => {
    const asked = (prefill || question).trim();
    if (!asked) return;

    setLoading(true);
    setError("");
    try {
      const res = await api.post("/chat/", { question: asked });
      setResponse({ ...res.data, askedQuestion: asked });
      setAutoPack(res.data.auto_resources || []);
      setQuestion("");
      const latest = await api.get("/chat/history");
      setHistory(latest.data);
    } catch (err) {
      setError(err.response?.data?.error || "Chatbot request failed.");
    } finally {
      setLoading(false);
    }
  };

  const downloadContent = async (contentType, topic, baseText) => {
    setDownloadError("");
    try {
      const res = await api.post("/downloads/", {
        content_type: contentType,
        topic: topic || response?.askedQuestion || history[0]?.question || "learning concept",
        content: "",
        base_content: baseText || response?.text || "",
      });
      const fileResp = await api.get(`/downloads/file/${res.data.download_id}`, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `chat_${contentType}_${Date.now()}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.error || "Failed to download file.");
    }
  };

  const downloadById = async (downloadId, label) => {
    setDownloadError("");
    try {
      const fileResp = await api.get(`/downloads/file/${downloadId}`, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = label || `resource_${downloadId}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.error || "Failed to download file.");
    }
  };

  const openPracticeForTopic = (topic) => {
    const cleanTopic = (topic || response?.askedQuestion || question || "").trim();
    if (!cleanTopic) return;
    navigate(`/practice?topic=${encodeURIComponent(cleanTopic)}`);
  };

  return (
    <>
      <NavBar />
      <div className="container pb-5">
        <div className="chatbot-layout">
          <section className="glass-card p-3 p-md-4 chatbot-main">
            <div className="chatbot-header mb-3">
              <div>
                <h4 className="mb-1">AI Chatbot</h4>
                <p className="text-muted mb-0">Learning mode: <strong>{formatStyle(style)}</strong></p>
              </div>
              <span className={`badge ${response?.ai_used ? "text-bg-success" : "text-bg-secondary"}`}>
                {response ? (response.ai_used ? "AI-generated" : "Fallback") : "Ready"}
              </span>
            </div>

            {error && <div className="alert alert-danger py-2">{error}</div>}
            {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}

            <div className="chat-window mb-3">
              {conversation.length === 0 ? (
                <div className="chat-empty text-muted">
                  Start by asking a topic. Responses are adapted to your learning style.
                </div>
              ) : (
                conversation.map((msg) => (
                  <div key={msg.id} className={`chat-msg ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}>
                    <div className="chat-bubble">
                      {msg.role === "assistant" && msg.responseType && (
                        <small className="chat-meta">{msg.responseType} response</small>
                      )}
                      <pre className="chat-text">{msg.text}</pre>
                      {msg.role === "assistant" && (
                        <div className="d-flex flex-wrap gap-2 mt-2">
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => openPracticeForTopic(msg.sourceQuestion)}
                          >
                            Practice This Topic
                          </button>
                          <button
                            className="btn btn-sm btn-outline-warning"
                            onClick={() => downloadContent("task_sheet", msg.sourceQuestion, msg.text)}
                          >
                            Download Task
                          </button>
                          <button
                            className="btn btn-sm btn-outline-success"
                            onClick={() => downloadContent("solution", msg.sourceQuestion, msg.text)}
                          >
                            Download Solution
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {response && (
              <div className="asset-panel mb-3">
                <h6 className="mb-2">Latest Response Assets</h6>
                {response.assets?.diagram && <p className="mb-1"><strong>Diagram:</strong> {response.assets.diagram}</p>}
                {response.assets?.video_url && <p className="mb-1"><a href={response.assets.video_url} target="_blank" rel="noreferrer">Open Video</a></p>}
                {response.assets?.gif_url && <img src={response.assets.gif_url} alt="visual gif" className="asset-image" />}
                {response.assets?.audio_url && <audio controls src={response.assets.audio_url} className="w-100 mt-2" />}
                {response.assets?.starter_code && <pre className="chat-text mt-2">{response.assets.starter_code}</pre>}
                {autoPack.length > 0 && (
                  <div className="mt-3">
                    <p className="mb-2"><strong>Auto AI Learning Pack</strong></p>
                    <div className="d-flex flex-wrap gap-2">
                      {autoPack.map((item) => (
                        <button
                          key={item.download_id}
                          className="btn btn-sm btn-outline-dark"
                          onClick={() => downloadById(item.download_id, `${item.content_type}_${item.download_id}`)}
                        >
                          Download {item.content_type}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="composer">
              <textarea
                className="form-control"
                rows={2}
                placeholder="Ask anything..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    ask();
                  }
                }}
              />
              <button className="btn brand-btn text-white" onClick={() => ask()} disabled={loading}>
                {loading ? "Thinking..." : "Ask"}
              </button>
              <button
                className="btn btn-outline-primary"
                onClick={() => openPracticeForTopic()}
                disabled={loading && !response}
              >
                Open Practice
              </button>
            </div>
          </section>

          <aside className="glass-card p-3 p-md-4 chatbot-side">
            <h6 className="mb-2">Quick Ask</h6>
            <div className="d-flex flex-wrap gap-2 mb-4">
              {QUICK_PROMPTS.map((p) => (
                <button key={p} className="btn btn-sm btn-outline-secondary" onClick={() => ask(p)} disabled={loading}>
                  {p}
                </button>
              ))}
            </div>

            <h6 className="mb-2">Download Options</h6>
            <div className="d-grid gap-2 mb-4">
              {style === "visual" && (
                <>
                  <button className="btn btn-sm btn-outline-primary" onClick={() => downloadContent("pdf")} disabled={!response}>Download Notes</button>
                  <button className="btn btn-sm btn-outline-primary" onClick={() => downloadContent("video")} disabled={!response}>Download Video Summary</button>
                </>
              )}
              {style === "auditory" && (
                <button className="btn btn-sm btn-outline-success" onClick={() => downloadContent("audio")} disabled={!response}>Download Audio Script</button>
              )}
              <button className="btn btn-sm btn-outline-warning" onClick={() => downloadContent("task_sheet")} disabled={!response}>Download Task Sheet</button>
              <button className="btn btn-sm btn-outline-warning" onClick={() => downloadContent("solution")} disabled={!response}>Download Solution</button>
            </div>

            <h6 className="mb-2">Recent Questions</h6>
            {history.length === 0 ? (
              <p className="text-muted mb-0">No history yet.</p>
            ) : (
              <ul className="list-unstyled mb-0 small">
                {history.slice(0, 8).map((h) => (
                  <li key={h.chat_id} className="mb-2">
                    <button className="btn btn-link p-0 text-start" onClick={() => setQuestion(h.question)}>
                      {h.question}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </aside>
        </div>
      </div>
    </>
  );
}
