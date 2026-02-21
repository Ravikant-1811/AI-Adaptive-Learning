import { useEffect, useState } from "react";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function ChatbotPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [history, setHistory] = useState([]);
  const [style, setStyle] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/style/mine").then((res) => setStyle(res.data.learning_style));
    api.get("/chat/history").then((res) => setHistory(res.data));
  }, []);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await api.post("/chat/", { question });
      setResponse(res.data);
      setQuestion("");
      const latest = await api.get("/chat/history");
      setHistory(latest.data);
    } finally {
      setLoading(false);
    }
  };

  const downloadContent = async (contentType) => {
    if (!response?.text) return;
    const payload = [response.text, JSON.stringify(response.assets || {}, null, 2)].join("\n\n");
    const res = await api.post("/downloads/", {
      content_type: contentType,
      content: payload,
    });
    const fullUrl = `${import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api"}${res.data.download_url}`;
    window.open(fullUrl, "_blank");
  };

  return (
    <>
      <NavBar />
      <div className="container pb-5">
        <div className="glass-card p-4 mb-4">
          <h4>AI Chatbot</h4>
          <p className="text-muted mb-2">Adaptive response mode: {style || "unknown"}</p>
          <div className="d-flex gap-2">
            <input
              className="form-control"
              placeholder="Ask a question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask()}
            />
            <button className="btn brand-btn text-white" onClick={ask} disabled={loading}>
              {loading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {response && (
            <div className="mt-4 border rounded p-3">
              <h6 className="text-uppercase">{response.response_type} response</h6>
              <pre className="mb-2" style={{ whiteSpace: "pre-wrap" }}>{response.text}</pre>

              {response.assets?.diagram && <p className="mb-1"><strong>Flow Diagram:</strong> {response.assets.diagram}</p>}
              {response.assets?.video_url && (
                <p className="mb-1">
                  <strong>Video:</strong> <a href={response.assets.video_url} target="_blank" rel="noreferrer">Open visual explanation</a>
                </p>
              )}
              {response.assets?.gif_url && (
                <img src={response.assets.gif_url} alt="visual gif" style={{ maxWidth: "100%", borderRadius: 8 }} />
              )}
              {response.assets?.audio_url && (
                <div className="mt-2">
                  <audio controls src={response.assets.audio_url} style={{ width: "100%" }} />
                </div>
              )}
              {response.assets?.audio_script && (
                <p className="mb-1 mt-2"><strong>Audio Script:</strong> {response.assets.audio_script}</p>
              )}
              {response.assets?.starter_code && <pre style={{ whiteSpace: "pre-wrap" }}>{response.assets.starter_code}</pre>}

              <div className="d-flex gap-2 mt-2">
                {style === "visual" && (
                  <>
                    <button className="btn btn-sm btn-outline-primary" onClick={() => downloadContent("pdf")}>Download Notes</button>
                    <button className="btn btn-sm btn-outline-primary" onClick={() => downloadContent("video")}>Download Video Summary</button>
                  </>
                )}
                {style === "auditory" && (
                  <button className="btn btn-sm btn-outline-success" onClick={() => downloadContent("audio")}>Download Audio Script</button>
                )}
                {style === "kinesthetic" && (
                  <>
                    <button className="btn btn-sm btn-outline-warning" onClick={() => downloadContent("task_sheet")}>Download Task Sheet</button>
                    <button className="btn btn-sm btn-outline-warning" onClick={() => downloadContent("solution")}>Download Solution</button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="glass-card p-4">
          <h5>Recent Chat History</h5>
          {history.length === 0 ? (
            <p className="text-muted mb-0">No history yet.</p>
          ) : (
            <ul className="mb-0">
              {history.map((h) => (
                <li key={h.chat_id}>{h.question} ({h.learning_style_used})</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
