import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

const QUICK_PROMPTS = [
  "Explain Java basics for beginners",
  "How does try-catch-finally work?",
  "Give me one practical coding task",
  "What are common mistakes in Java?",
];
const CHAT_LATEST_RESPONSE_KEY = "chatLatestRichResponse";
const EXT_BY_TYPE = {
  pdf: ".txt",
  video: ".txt",
  audio: ".mp3",
  task_sheet: ".txt",
  solution: ".txt",
};

function formatStyle(style) {
  if (!style) return "Unknown";
  return style.charAt(0).toUpperCase() + style.slice(1);
}

function safeFileName(name) {
  return String(name || "resource")
    .replace(/[^a-zA-Z0-9._-]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 80) || "resource";
}

function shortTime(isoText) {
  if (!isoText) return "";
  const dt = new Date(isoText);
  if (Number.isNaN(dt.getTime())) return "";
  return dt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
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
  const [quickPrompts, setQuickPrompts] = useState(QUICK_PROMPTS);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackMsg, setFeedbackMsg] = useState("");
  const [selectedHistoryId, setSelectedHistoryId] = useState(null);

  const loadPrompts = async (topic = "") => {
    try {
      const res = await api.get("/chat/suggestions", { params: { topic } });
      const prompts = Array.isArray(res.data?.prompts) ? res.data.prompts : [];
      setQuickPrompts(prompts.length ? prompts : QUICK_PROMPTS);
    } catch {
      setQuickPrompts(QUICK_PROMPTS);
    }
  };

  const loadInitial = async () => {
    setBootLoading(true);
    setError("");
    try {
      const [styleRes, historyRes] = await Promise.all([api.get("/style/mine"), api.get("/chat/history")]);
      setStyle(styleRes.data.learning_style || null);
      const rows = historyRes.data || [];
      setHistory(rows);
      setSelectedHistoryId(rows?.[0]?.chat_id ?? null);
      const latestTopic = rows?.[0]?.question || "";
      await loadPrompts(latestTopic);

      const cachedRaw = localStorage.getItem(CHAT_LATEST_RESPONSE_KEY);
      if (cachedRaw) {
        try {
          const cached = JSON.parse(cachedRaw);
          setResponse(cached || null);
          setAutoPack(Array.isArray(cached?.auto_resources) ? cached.auto_resources : []);
        } catch {
          localStorage.removeItem(CHAT_LATEST_RESPONSE_KEY);
          setResponse(null);
          setAutoPack([]);
        }
      } else {
        setResponse(null);
        setAutoPack([]);
      }
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
      const richResponse = { ...res.data, askedQuestion: asked };
      setResponse(richResponse);
      setFeedbackComment("");
      setFeedbackMsg("");
      await loadPrompts(asked);
      setAutoPack(res.data.auto_resources || []);
      localStorage.setItem(CHAT_LATEST_RESPONSE_KEY, JSON.stringify(richResponse));
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
          // optional asset
        }
      } else if ((style || "").toLowerCase() === "auditory") {
        try {
          const created = await api.post("/downloads/", {
            content_type: "audio",
            topic: asked,
            content: "",
            base_content: res.data?.text || "",
          });
          const fileResp = await api.get(`/downloads/file/${created.data.download_id}`, { responseType: "blob" });
          const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
          setAudioSrc(blobUrl);
        } catch {
          setError("Audio generation failed. Please try again.");
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
      setSelectedHistoryId((latest.data || [])[0]?.chat_id ?? null);
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
      setSelectedHistoryId(null);
      setResponse(null);
      setAutoPack([]);
      localStorage.removeItem(CHAT_LATEST_RESPONSE_KEY);
      localStorage.removeItem("linkedPracticeBundle");
    } catch {
      setError("Failed to clear chat history.");
    }
  };

  const startNewChat = () => {
    setQuestion("");
    setSelectedHistoryId(null);
    setResponse(null);
    setAutoPack([]);
    setFeedbackComment("");
    setFeedbackMsg("");
    localStorage.removeItem(CHAT_LATEST_RESPONSE_KEY);
  };

  const downloadById = async (downloadId, label, contentType = "") => {
    setDownloadError("");
    try {
      const fileResp = await api.get(`/downloads/file/${downloadId}`, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      const ext = EXT_BY_TYPE[contentType] || "";
      const base = safeFileName(label || `resource_${downloadId}`);
      link.download = base.endsWith(ext) ? base : `${base}${ext}`;
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

  const submitFeedback = async (rating) => {
    if (!response?.chat_id) return;
    setFeedbackMsg("");
    try {
      await api.post("/chat/feedback", {
        chat_id: response.chat_id,
        rating,
        comment: feedbackComment.trim(),
      });
      setFeedbackMsg(rating === 1 ? "Marked as helpful." : "Marked as needs improvement.");
      const latest = await api.get("/chat/history");
      setHistory(latest.data || []);
      setSelectedHistoryId((latest.data || [])[0]?.chat_id ?? null);
    } catch (err) {
      setFeedbackMsg(err.response?.data?.error || "Failed to save feedback.");
    }
  };

  const focusHistoryMessage = (chatId, questionText = "") => {
    setSelectedHistoryId(chatId);
    if (questionText) setQuestion(questionText);
    setTimeout(() => {
      const target = document.getElementById(`q-${chatId}`) || document.getElementById(`a-${chatId}`);
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 60);
  };


  return (
    <>
      <NavBar />
      <div className="container page-wrap">
        <div className="vak-chat-shell mt-3">
          <aside className="vak-sidebar">
            <div className="vak-logo mb-3">
              <span className="brand-mark">AL</span>
              <div>
                <div className="fw-bold">Adaptive Learning</div>
                <small className="text-muted">AI Tutor</small>
              </div>
            </div>

            <button className="btn brand-btn w-100 mb-3" onClick={startNewChat} disabled={loading || bootLoading}>
              + New Chat
            </button>

            <div className="vak-history-list flex-grow-1">
              {history.length === 0 ? (
                <div className="text-muted small">No chat history yet.</div>
              ) : (
                history.map((h) => (
                  <button
                    key={h.chat_id}
                    className={`vak-history-item text-start ${selectedHistoryId === h.chat_id ? "active" : ""}`}
                    onClick={() => focusHistoryMessage(h.chat_id, h.question)}
                    type="button"
                  >
                    <div className="vak-history-title">{h.question}</div>
                    <small className="text-muted">{shortTime(h.timestamp) || "recent"}</small>
                  </button>
                ))
              )}
            </div>

            <div className="pt-3 mt-3 border-top">
              <small className="text-muted d-block">Learning Mode</small>
              <strong>{formatStyle(style)}</strong>
            </div>
          </aside>

          <section className="vak-chat-main">
            <div className="vak-chat-topbar">
              <div className="vak-mode-pills">
                <span className={`pill ${style === "visual" ? "active" : ""}`}>Visual</span>
                <span className={`pill ${style === "auditory" ? "active" : ""}`}>Auditory</span>
                <span className={`pill ${style === "kinesthetic" ? "active" : ""}`}>Kinesthetic</span>
              </div>
              <div className="d-flex gap-2">
                <button
                  className="btn btn-sm surface-btn"
                  onClick={() => loadPrompts(question || response?.askedQuestion || "")}
                  disabled={loading || bootLoading}
                >
                  New Suggestions
                </button>
                <button className="btn btn-sm surface-btn" onClick={clearChat} disabled={loading || bootLoading}>
                  Clear Chat
                </button>
              </div>
            </div>

            <div ref={chatWindowRef} className="vak-chat-window p-3">
              {error && <div className="alert alert-danger py-2">{error}</div>}
              {downloadError && <div className="alert alert-danger py-2">{downloadError}</div>}

              {bootLoading ? (
                <div className="vak-empty-state">Loading chat...</div>
              ) : conversation.length === 0 ? (
                <div className="vak-empty-state">
                  <h4 className="mb-2">Welcome to Adaptive Chat</h4>
                  <p className="text-muted mb-3">Ask a question and get style-based explanation, downloads, and practice tasks.</p>
                  <div className="vak-quick-grid">
                    {quickPrompts.map((p) => (
                      <button key={p} className="btn surface-btn text-start" onClick={() => ask(p)}>
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {conversation.map((msg) => (
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
                  ))}
                  {loading && <div className="text-muted small px-2 pb-2">Thinking...</div>}
                </>
              )}
            </div>

            {(response?.practice?.tasks?.length > 0 || response?.assets) && (
              <div className="p-3" style={{ borderTop: "1px solid var(--line)", background: "#fbfbfe" }}>
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
                            onClick={() => downloadById(item.download_id, `${item.content_type}_${item.download_id}`, item.content_type)}
                          >
                            Download {item.content_type}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {response?.assets && (
                  <div className="asset-panel">
                    <h6 className="mb-2">Learning-Style Assets</h6>
                    {response.assets.diagram && <p className="mb-2"><strong>Flow:</strong> {response.assets.diagram}</p>}
                    {response.assets.ai_image_url && (
                      <a href={response.assets.ai_image_url} target="_blank" rel="noreferrer">
                        <img src={response.assets.ai_image_url} alt="ai generated learning visual" className="asset-image asset-image-hero mb-2" />
                      </a>
                    )}
                    {(response.assets.graph_image_url || response.assets.bar_graph_image_url || response.assets.flowchart_image_url || response.assets.topic_image_url || response.assets.gif_url) && (
                      <div className="visual-gallery mb-2">
                        {response.assets.topic_image_url && (
                          <a href={response.assets.topic_image_url} target="_blank" rel="noreferrer">
                            <img src={response.assets.topic_image_url} alt="visual concept map" className="asset-image" />
                          </a>
                        )}
                        {response.assets.graph_image_url && (
                          <a href={response.assets.graph_image_url} target="_blank" rel="noreferrer">
                            <img src={response.assets.graph_image_url} alt="visual radar graph" className="asset-image" />
                          </a>
                        )}
                        {response.assets.bar_graph_image_url && (
                          <a href={response.assets.bar_graph_image_url} target="_blank" rel="noreferrer">
                            <img src={response.assets.bar_graph_image_url} alt="visual bar graph" className="asset-image" />
                          </a>
                        )}
                        {response.assets.flowchart_image_url && (
                          <a href={response.assets.flowchart_image_url} target="_blank" rel="noreferrer">
                            <img src={response.assets.flowchart_image_url} alt="visual flowchart" className="asset-image" />
                          </a>
                        )}
                        {response.assets.gif_url && (
                          <a href={response.assets.gif_url} target="_blank" rel="noreferrer">
                            <img src={response.assets.gif_url} alt="visual gif" className="asset-image" />
                          </a>
                        )}
                      </div>
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

                    {response.chat_id && (
                      <div className="mt-3">
                        <p className="mb-1"><strong>Response Quality Feedback</strong></p>
                        <div className="d-flex flex-wrap gap-2 mb-2">
                          <button className="btn btn-sm surface-btn" onClick={() => submitFeedback(1)}>Helpful</button>
                          <button className="btn btn-sm surface-btn" onClick={() => submitFeedback(-1)}>Needs Improvement</button>
                        </div>
                        <textarea
                          className="form-control"
                          rows={2}
                          placeholder="Optional comment to improve future responses..."
                          value={feedbackComment}
                          onChange={(e) => setFeedbackComment(e.target.value)}
                        />
                        {feedbackMsg && <small className="text-muted d-block mt-1">{feedbackMsg}</small>}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            <div className="vak-composer-wrap">
              <div className="vak-composer">
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
          </section>
        </div>
      </div>
    </>
  );
}
