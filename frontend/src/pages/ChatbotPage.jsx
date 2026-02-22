import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

const QUICK_PROMPTS = [
  "Explain exception handling in Java",
  "How does try-catch-finally work?",
  "Difference between interface and abstract class",
  "Give me a beginner Java debugging task",
];

function formatStyle(style) {
  if (!style) return "Unknown";
  return style.charAt(0).toUpperCase() + style.slice(1);
}

export default function ChatbotPage() {
  const navigate = useNavigate();
  const chatWindowRef = useRef(null);

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
    api.get("/chat/history").then((res) => setHistory(res.data || []));
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
        sourceQuestion: h.question,
        timestamp: h.timestamp,
      },
    ]);
  }, [history]);

  useEffect(() => {
    const node = chatWindowRef.current;
    if (!node) return;
    node.scrollTop = node.scrollHeight;
  }, [conversation.length, loading]);

  const ask = async (prefill) => {
    const asked = (prefill || question).trim();
    if (!asked) return;

    setLoading(true);
    setError("");
    try {
      const res = await api.post("/chat/", { question: asked });
      setResponse({ ...res.data, askedQuestion: asked });
      setAutoPack(res.data.auto_resources || []);

      if (res.data?.practice?.topic && Array.isArray(res.data?.practice?.tasks)) {
        localStorage.setItem(
          "linkedPracticeBundle",
          JSON.stringify({
            topic: res.data.practice.topic,
            source: res.data.practice.source || "chat",
            tasks: res.data.practice.tasks,
            saved_at: Date.now(),
          })
        );
      }

      setQuestion("");
      const latest = await api.get("/chat/history");
      setHistory(latest.data || []);
    } catch (err) {
      setError(err.response?.data?.error || "Chatbot request failed.");
    } finally {
      setLoading(false);
    }
  };

  const clearLocalChat = () => {
    setHistory([]);
    setResponse(null);
    setAutoPack([]);
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

  const openPracticeForTopic = (topic, taskName = "") => {
    const cleanTopic = (topic || response?.askedQuestion || question || "").trim();
    if (!cleanTopic) return;
    const taskQuery = taskName ? `&task=${encodeURIComponent(taskName)}` : "";
    navigate(`/practice?topic=${encodeURIComponent(cleanTopic)}${taskQuery}`);
  };

  return (
    <>
      <NavBar />
      <div className="container-fluid page-wrap px-3 px-md-4">
        <div className="vak-chat-shell">
          <aside className="vak-sidebar">
            <div className="vak-logo mb-3">
              <span className="brand-mark">AL</span>
              <div>
                <h5 className="mb-0">VAKify</h5>
                <small className="text-muted">Adaptive AI Tutor</small>
              </div>
            </div>

            <button className="btn vak-gradient-btn w-100 mb-3" onClick={clearLocalChat}>+ New Chat</button>

            <div className="vak-history-list">
              {history.length === 0 ? (
                <div className="vak-history-item active">
                  <h6 className="mb-1">New Chat</h6>
                  <p className="mb-1 text-muted">Start a new conversation</p>
                  <small>Just now</small>
                </div>
              ) : (
                history.slice(0, 8).map((h, idx) => (
                  <button
                    key={h.chat_id}
                    className={`vak-history-item ${idx === 0 ? "active" : ""}`}
                    onClick={() => setQuestion(h.question)}
                  >
                    <h6 className="mb-1 text-start">{h.question}</h6>
                    <small>{new Date(h.timestamp).toLocaleTimeString()}</small>
                  </button>
                ))
              )}
            </div>
          </aside>

          <section className="vak-chat-main">
            <div className="vak-chat-topbar">
              <div className="d-flex align-items-center gap-3 flex-wrap">
                <h5 className="mb-0">Learning Mode:</h5>
                <div className="vak-mode-pills">
                  <span className={`pill ${style === "visual" ? "active" : ""}`}>Visual</span>
                  <span className={`pill ${style === "auditory" ? "active" : ""}`}>Auditory</span>
                  <span className={`pill ${style === "kinesthetic" ? "active" : ""}`}>Kinesthetic</span>
                </div>
              </div>
              <button className="btn btn-sm surface-btn" onClick={clearLocalChat}>Clear Chat</button>
            </div>

            {error && <div className="alert alert-danger py-2 m-3 mb-0">{error}</div>}
            {downloadError && <div className="alert alert-danger py-2 m-3 mb-0">{downloadError}</div>}

            <div ref={chatWindowRef} className="vak-chat-window">
              {conversation.length === 0 ? (
                <div className="vak-empty-state">
                  <div className="brand-mark" style={{ width: 80, height: 80, borderRadius: 24, fontSize: 24 }}>AL</div>
                  <h2 className="mt-3 mb-2">Welcome to VAKify</h2>
                  <p className="text-muted mb-3">Start learning with AI explanations tailored to your {formatStyle(style)} learning style.</p>
                  <div className="vak-quick-grid">
                    {QUICK_PROMPTS.map((p) => (
                      <button key={p} className="btn surface-btn text-start" onClick={() => ask(p)}>{p}</button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-3">
                  {conversation.map((msg) => (
                    <div key={msg.id} className={`chat-msg ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}>
                      <div className="chat-bubble">
                        {msg.role === "assistant" && msg.responseType && (
                          <small className="chat-meta">{msg.responseType} response</small>
                        )}
                        <pre className="chat-text">{msg.text}</pre>

                        {msg.role === "assistant" && (
                          <div className="d-flex flex-wrap gap-2 mt-2">
                            <button className="btn btn-sm surface-btn" onClick={() => openPracticeForTopic(msg.sourceQuestion)}>
                              Practice This Topic
                            </button>
                            <button className="btn btn-sm surface-btn" onClick={() => downloadContent("task_sheet", msg.sourceQuestion, msg.text)}>
                              Download Task
                            </button>
                            <button className="btn btn-sm surface-btn" onClick={() => downloadContent("solution", msg.sourceQuestion, msg.text)}>
                              Download Solution
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {response && response.practice?.tasks?.length > 0 && (
              <div className="asset-panel m-3">
                <h6 className="mb-2">Assigned Practice Tasks ({response.practice.source})</h6>
                <div className="d-flex flex-wrap gap-2 mb-2">
                  <button className="btn btn-sm vak-gradient-btn" onClick={() => openPracticeForTopic(response.practice.topic)}>
                    Start Topic Practice
                  </button>
                  {response.practice.tasks.map((task) => (
                    <button
                      key={`start-${task.task_name}`}
                      className="btn btn-sm surface-btn"
                      onClick={() => openPracticeForTopic(response.practice.topic, task.task_name)}
                    >
                      Start: {task.task_name}
                    </button>
                  ))}
                </div>
                {autoPack.length > 0 && (
                  <div className="d-flex flex-wrap gap-2">
                    {autoPack.map((item) => (
                      <button
                        key={item.download_id}
                        className="btn btn-sm surface-btn"
                        onClick={() => downloadById(item.download_id, `${item.content_type}_${item.download_id}`)}
                      >
                        Download {item.content_type}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="vak-composer-wrap">
              <div className="vak-composer">
                <textarea
                  className="form-control"
                  rows={1}
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
                <button className="btn vak-gradient-btn" onClick={() => ask()} disabled={loading}>
                  {loading ? "Thinking..." : "Send"}
                </button>
              </div>
              <small className="text-muted">Press Enter to send • Shift + Enter for new line</small>
            </div>
          </section>
        </div>
      </div>
    </>
  );
}
