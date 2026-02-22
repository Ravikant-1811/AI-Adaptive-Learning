import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function LearningStylePage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("select");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [source, setSource] = useState("default");
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const loadDefaultQuestions = async () => {
    const res = await api.get("/style/questions");
    setQuestions(res.data.questions || []);
    setSource("default");
    setCurrentIndex(0);
  };

  const generateAiQuestions = async (force = false) => {
    if (loadingQuestions) return;
    if (!force && mode !== "test") return;
    setLoadingQuestions(true);
    setError("");
    setResult(null);
    setAnswers({});
    setCurrentIndex(0);
    try {
      const res = await api.post("/style/generate-questions", {
        question_count: 20,
      });
      setQuestions(res.data.questions || []);
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
    } catch (err) {
      setError(err.response?.data?.error || "Unable to submit test.");
    } finally {
      setSubmitting(false);
    }
  };

  const currentQuestion = questions[currentIndex] || null;
  const progress = questions.length ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

  const nextQuestion = () => {
    if (!currentQuestion) return;
    if (!answers[currentQuestion.id]) {
      setError("Please choose one option to continue.");
      return;
    }
    setError("");
    setCurrentIndex((prev) => Math.min(prev + 1, questions.length - 1));
  };

  const prevQuestion = () => {
    setError("");
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const styleCards = [
    {
      key: "visual",
      title: "Visual",
      tips: [
        "Use diagrams, charts, and mind maps for studying",
        "Color-code your notes and materials",
        "Watch educational videos and visual demonstrations",
      ],
    },
    {
      key: "auditory",
      title: "Auditory",
      tips: [
        "Listen to lectures and audio recordings",
        "Discuss topics with study groups",
        "Read your notes out loud",
      ],
    },
    {
      key: "kinesthetic",
      title: "Kinesthetic",
      tips: [
        "Take frequent breaks to move around",
        "Use hands-on activities and experiments",
        "Act out concepts or use role-playing",
      ],
    },
  ];

  return (
    <>
      <NavBar />
      <div className="container page-wrap" style={{ maxWidth: 980 }}>
        <header className="page-header">
          <p className="page-kicker mb-1">Discover your learning style</p>
          <h2 className="page-title">VAKify Assessment</h2>
          <p className="page-subtitle">Identify how you learn best and get personalized recommendations.</p>
        </header>

        <div className="glass-card p-4">
          <div className="d-flex flex-wrap gap-2 mb-3">
            <button className={`btn ${mode === "select" ? "brand-btn" : "surface-btn"}`} onClick={() => setMode("select")}>Direct Selection</button>
            <button className={`btn ${mode === "test" ? "brand-btn" : "surface-btn"}`} onClick={() => setMode("test")}>Take Assessment Test</button>
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

              {result ? (
                <div className="soft-card p-4">
                  <h5 className="mb-3">Personalized Learning Recommendations</h5>
                  <div className="recommend-grid mb-3">
                    {styleCards.map((item) => {
                      const score =
                        item.key === "visual"
                          ? result.visual_score
                          : item.key === "auditory"
                            ? result.auditory_score
                            : result.kinesthetic_score;
                      const isActive = result.learning_style === item.key;
                      return (
                        <article key={item.key} className={`recommend-card ${isActive ? "active" : ""}`}>
                          <h6 className="mb-1">{item.title}</h6>
                          <p className="text-muted mb-2">{score}/{questions.length} points</p>
                          <ul className="mb-0 small">
                            {item.tips.map((tip) => (
                              <li key={tip}>{tip}</li>
                            ))}
                          </ul>
                        </article>
                      );
                    })}
                  </div>
                  <button className="btn brand-btn" onClick={() => navigate("/dashboard")}>
                    Go to Dashboard
                  </button>
                </div>
              ) : (
                <>
                  <div className="quiz-progress mb-3">
                    <div className="d-flex justify-content-between mb-1">
                      <strong>Question {Math.min(currentIndex + 1, questions.length)} of {questions.length}</strong>
                      <span>{progress}%</span>
                    </div>
                    <div className="progress" style={{ height: 10 }}>
                      <div className="progress-bar" style={{ width: `${progress}%` }} />
                    </div>
                  </div>

                  <div className="soft-card p-3 mb-3 d-flex justify-content-between align-items-center">
                    <small className="text-muted mb-0">
                      Question source: <strong>{source === "ai" ? "AI-generated" : "Default fallback"}</strong>
                    </small>
                    <button className="btn btn-sm surface-btn" onClick={() => generateAiQuestions(true)} disabled={loadingQuestions}>
                      {loadingQuestions ? "Generating..." : "Regenerate Questions"}
                    </button>
                  </div>

                  {loadingQuestions && <div className="alert alert-info py-2">Generating AI questions...</div>}

                  {currentQuestion && (
                    <div className="quiz-card soft-card p-4">
                      <h4 className="mb-4">{currentQuestion.question}</h4>
                      <div className="d-grid gap-3">
                        {currentQuestion.options.map((opt) => {
                          const active = answers[currentQuestion.id] === opt.style;
                          return (
                            <button
                              key={opt.key}
                              className={`quiz-option ${active ? "active" : ""}`}
                              onClick={() => setAnswers((prev) => ({ ...prev, [currentQuestion.id]: opt.style }))}
                            >
                              {opt.text}
                            </button>
                          );
                        })}
                      </div>

                      <div className="d-flex justify-content-between mt-4">
                        <button className="btn surface-btn" disabled={currentIndex === 0} onClick={prevQuestion}>
                          Previous
                        </button>

                        {currentIndex < questions.length - 1 ? (
                          <button className="btn brand-btn" onClick={nextQuestion}>Next</button>
                        ) : (
                          <button
                            className="btn brand-btn"
                            onClick={submitTest}
                            disabled={loadingQuestions || submitting || questions.length < 10}
                          >
                            {submitting ? "Submitting..." : "Finish Test"}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
}
