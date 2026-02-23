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
  const [bootLoading, setBootLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadError, setDownloadError] = useState("");
  const [autoPack, setAutoPack] = useState([]);
  const [audioSrc, setAudioSrc] = useState("");

  const loadInitial = async () => {
    setBootLoading(true);
    setError("");
    try {
      const [styleRes, historyRes] = await Promise.all([api.get("/style/mine"), api.get("/chat/history")]);
      setStyle(styleRes.data.learning_style || null);
      setHistory(historyRes.data || []);
    } catch {
      setError("Failed to load chat. Please refresh.");
    } finally {
      setBootLoading(false);
    }
  };

  useEffect(() => {
    loadInitial();
  }, []);

  const conversation = useMemo(() => {
    const rows = [...history].reverse();
    return rows.flatMap((h) => [
      { id: `q-${h.chat_id}`, role: "user", text: h.question, timestamp: h.timestamp },
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

  useEffect(() => {
    return () => {
      if (audioSrc) {
        window.URL.revokeObjectURL(audioSrc);
      }
    };
  }, [audioSrc]);

  const ask = async (prefill) => {
    const asked = (prefill || question).trim();
    if (!asked || loading) return;

    setLoading(true);
    setError("");
    try {
      const res = await api.post("/chat/", { question: asked });
      setResponse({ ...res.data, askedQuestion: asked });
      setAutoPack(res.data.auto_resources || []);
      if (audioSrc) {
        window.URL.revokeObjectURL(audioSrc);
        setAudioSrc("");
      }

      if (res.data?.audio_download_id) {
        try {
          const fileResp = await api.get(`/downloads/file/${res.data.audio_download_id}`, { responseType: "blob" });
          const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
          setAudioSrc(blobUrl);
        } catch {
          // no-op, audio remains optional
        }
      }

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

  const clearChat = async () => {
    setError("");
    try {
      await api.delete("/chat/history");
      setHistory([]);
      setResponse(null);
      setAutoPack([]);
      localStorage.removeItem("linkedPracticeBundle");
    } catch {
      setError("Failed to clear chat history.");
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
      <div className="container page-wrap">
        <header className="page-header">
          <p className="page-kicker mb-1">AI Learning Assistant</p>
          <h2 className="page-title">Adaptive Chat Workspace</h2>
          <p className="page-subtitle">Mode: <strong>{formatStyle(style)}</strong> | Ask, learn, then jump to synced practice.</p>
        </header>

        <div className="glass-card p-3 p-md-4">
          <div className="d-flex justify-content-between align-items-center mb-3 gap-2 flex-wrap">
            <div className="d-flex gap-2 flex-wrap">
              {QUICK_PROMPTS.map((p) => (
                <button key={p} className="btn btn-sm surface-btn" onClick={() => ask(p)} disabled={loading || bootLoading}>
                  {p}
                </button>
              ))}
            </div>
            <button className="btn btn-sm surface-btn" onClick={clearChat} disabled={loading || bootLoading}>Clear Chat</button>
          </div>

          {error && <div className="alert alert-danger py-2">{error}</div>}
          {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}

          <div ref={chatWindowRef} className="chat-window mb-3" style={{ height: "52vh" }}>
            {bootLoading ? (
              <div className="chat-empty">Loading chat...</div>
            ) : conversation.length === 0 ? (
              <div className="chat-empty">Start by asking a concept. You will get adaptive explanation + linked tasks.</div>
            ) : (
              conversation.map((msg) => (
                <div key={msg.id} className={`chat-msg ${msg.role === "user" ? "chat-user" : "chat-assistant"}`}>
                  <div className="chat-bubble">
                    {msg.role === "assistant" && msg.responseType && <small className="chat-meta">{msg.responseType} response</small>}
                    <pre className="chat-text">{msg.text}</pre>
                    {msg.role === "assistant" && (
                      <div className="d-flex flex-wrap gap-2 mt-2">
                        <button className="btn btn-sm surface-btn" onClick={() => openPracticeForTopic(msg.sourceQuestion)}>
                          Practice This Topic
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {response?.practice?.tasks?.length > 0 && (
            <div className="asset-panel mb-3">
              <h6 className="mb-2">Assigned Practice Tasks ({response.practice.source})</h6>
              <div className="d-flex flex-wrap gap-2 mb-2">
                <button className="btn btn-sm brand-btn" onClick={() => openPracticeForTopic(response.practice.topic)}>
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

          {response?.assets && (
            <div className="asset-panel mb-3">
              <h6 className="mb-2">Learning-Style Assets</h6>
              {response.assets.diagram && <p className="mb-2"><strong>Flow:</strong> {response.assets.diagram}</p>}
              {response.assets.graph_image_url && (
                <img src={response.assets.graph_image_url} alt="visual graph" className="asset-image mb-2" />
              )}
              {response.assets.gif_url && (
                <img src={response.assets.gif_url} alt="visual gif" className="asset-image mb-2" />
              )}
              {response.assets.video_url && (
                <p className="mb-2"><a href={response.assets.video_url} target="_blank" rel="noreferrer">Open Video Explanation</a></p>
              )}
              {response.assets.audio_script && <pre className="chat-text mb-2">{response.assets.audio_script}</pre>}
              {audioSrc && (
                <div>
                  <p className="mb-1"><strong>Audio Explanation</strong></p>
                  <audio controls src={audioSrc} className="w-100" />
                </div>
              )}
              {response.assets.starter_code && <pre className="chat-text">{response.assets.starter_code}</pre>}
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
            <button className="btn brand-btn" onClick={() => ask()} disabled={loading || bootLoading || !question.trim()}>
              {loading ? "Thinking..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
