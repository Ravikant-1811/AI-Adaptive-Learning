import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function LearningStylePage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("select");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.get("/style/questions").then((res) => setQuestions(res.data.questions));
  }, []);

  const saveDirect = async (style) => {
    await api.post("/style/select", { learning_style: style });
    navigate("/dashboard");
  };

  const submitTest = async () => {
    setError("");
    const values = questions.map((q) => answers[q.id]);
    if (values.some((v) => !v)) {
      setError("Please answer all questions before submitting.");
      return;
    }

    try {
      const res = await api.post("/style/submit-test", { answers: values });
      setResult(res.data);
      setTimeout(() => navigate("/dashboard"), 1200);
    } catch (err) {
      setError(err.response?.data?.error || "Unable to submit test.");
    }
  };

  return (
    <>
      <NavBar />
      <div className="container pb-5" style={{ maxWidth: 920 }}>
        <div className="glass-card p-4">
          <h4 className="mb-2">Identify Your Learning Style</h4>
          <p className="text-muted">Choose direct selection or complete the 20-question psychological test.</p>

          <div className="d-flex gap-2 mb-3">
            <button className="btn btn-outline-primary" onClick={() => setMode("select")}>Direct Selection</button>
            <button className="btn btn-outline-secondary" onClick={() => setMode("test")}>Know Your Learning Style (Test)</button>
          </div>

          {mode === "select" && (
            <div className="d-flex flex-wrap gap-2">
              <button className="btn btn-primary" onClick={() => saveDirect("visual")}>Visual</button>
              <button className="btn btn-success" onClick={() => saveDirect("auditory")}>Auditory</button>
              <button className="btn btn-warning" onClick={() => saveDirect("kinesthetic")}>Kinesthetic</button>
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

              <div className="d-grid gap-3">
                {questions.map((q) => (
                  <div key={q.id} className="border rounded p-3">
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
              <button className="btn brand-btn text-white mt-3" onClick={submitTest}>Submit Test</button>
            </>
          )}
        </div>
      </div>
    </>
  );
}
