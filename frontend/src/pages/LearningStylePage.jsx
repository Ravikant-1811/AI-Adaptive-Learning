import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function LearningStylePage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("select");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [source, setSource] = useState("default");
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const loadDefaultQuestions = async () => {
    const res = await api.get("/style/questions");
    setQuestions(res.data.questions || []);
    setSource("default");
  };

  const generateAiQuestions = async (force = false) => {
    if (loadingQuestions) return;
    if (!force && mode !== "test") return;
    setLoadingQuestions(true);
    setError("");
    setResult(null);
    setAnswers({});
    try {
      const res = await api.post("/style/generate-questions", {
        question_count: 20,
      });
      setQuestions(res.data.questions);
      setSource(res.data.source || "default");
    } catch (err) {
      try {
        await loadDefaultQuestions();
        setError("AI question generation failed. Loaded default questions instead.");
      } catch {
        setError(err.response?.data?.error || "Unable to generate questions.");
      }
    } finally {
      setLoadingQuestions(false);
    }
  };

  useEffect(() => {
    if (mode === "test") {
      generateAiQuestions(true);
    }
  }, [mode]);

  const saveDirect = async (style) => {
    await api.post("/style/select", { learning_style: style });
    navigate("/dashboard");
  };

  const submitTest = async () => {
    setError("");
    if (loadingQuestions) {
      setError("Questions are still loading. Please wait.");
      return;
    }
    if (questions.length < 10) {
      setError("Questions not loaded yet. Please regenerate and try again.");
      return;
    }
    const values = questions.map((q) => answers[q.id]);
    if (values.some((v) => !v)) {
      setError("Please answer all questions before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      const res = await api.post("/style/submit-test", { answers: values });
      setResult(res.data);
      setTimeout(() => navigate("/dashboard"), 1200);
    } catch (err) {
      setError(err.response?.data?.error || "Unable to submit test.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <NavBar />
      <div className="container page-wrap" style={{ maxWidth: 980 }}>
        <header className="page-header">
          <p className="page-kicker mb-1">Personalization Setup</p>
          <h2 className="page-title">Identify Your Learning Style</h2>
          <p className="page-subtitle">Choose directly or run the AI-generated psychometric test for better adaptive results.</p>
        </header>

        <div className="glass-card p-4">
          <div className="d-flex flex-wrap gap-2 mb-3">
            <button className={`btn ${mode === "select" ? "brand-btn" : "surface-btn"}`} onClick={() => setMode("select")}>Direct Selection</button>
            <button className={`btn ${mode === "test" ? "brand-btn" : "surface-btn"}`} onClick={() => setMode("test")}>Know Your Learning Style (Test)</button>
          </div>

          {mode === "select" && (
            <div className="choice-grid">
              <article className="choice-card" onClick={() => saveDirect("visual")}>
                <h6 className="mb-1">Visual</h6>
                <p className="mb-0 text-muted">Diagrams, mapped steps, and flow understanding.</p>
              </article>
              <article className="choice-card" onClick={() => saveDirect("auditory")}>
                <h6 className="mb-1">Auditory</h6>
                <p className="mb-0 text-muted">Voice-guided explanations and spoken sequencing.</p>
              </article>
              <article className="choice-card" onClick={() => saveDirect("kinesthetic")}>
                <h6 className="mb-1">Kinesthetic</h6>
                <p className="mb-0 text-muted">Hands-on coding tasks with guided practice.</p>
              </article>
            </div>
          )}

          {mode === "test" && (
            <>
              {error && <div className="alert alert-danger py-2">{error}</div>}
              {result && (
                <div className="alert alert-success py-2">
                  Style detected: <strong>{result.learning_style}</strong> (V:{result.visual_score}, A:{result.auditory_score}, K:{result.kinesthetic_score})
                </div>
              )}
              <div className="soft-card p-3 mb-3 d-flex justify-content-between align-items-center">
                <small className="text-muted mb-0">
                  Question source: <strong>{source === "ai" ? "AI-generated" : "Default fallback"}</strong>
                </small>
                <button className="btn btn-sm surface-btn" onClick={() => generateAiQuestions(true)} disabled={loadingQuestions}>
                  {loadingQuestions ? "Generating..." : "Regenerate Questions"}
                </button>
              </div>

              {loadingQuestions && <div className="alert alert-info py-2">Generating AI questions...</div>}

              <div className="d-grid gap-3">
                {questions.map((q) => (
                  <div key={q.id} className="soft-card p-3">
                    <strong>{q.id}. {q.question}</strong>
                    <div className="mt-2 d-grid gap-2">
                      {q.options.map((opt) => (
                        <label key={opt.key} className="d-flex gap-2 align-items-start">
                          <input
                            type="radio"
                            name={`q-${q.id}`}
                            checked={answers[q.id] === opt.style}
                            onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt.style }))}
                          />
                          <span>{opt.text}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <button
                className="btn brand-btn mt-3"
                onClick={submitTest}
                disabled={loadingQuestions || submitting || questions.length < 10}
              >
                {submitting ? "Submitting..." : "Submit Test"}
              </button>
            </>
          )}
        </div>
      </div>
    </>
  );
}
