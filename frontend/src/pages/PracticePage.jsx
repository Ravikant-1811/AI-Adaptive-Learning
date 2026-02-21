import { useEffect, useState } from "react";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function PracticePage() {
  const [style, setStyle] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [code, setCode] = useState("");
  const [timeSpent, setTimeSpent] = useState(0);
  const [activities, setActivities] = useState([]);
  const [runOutput, setRunOutput] = useState({ stdout: "", stderr: "", status: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/style/mine").then((res) => setStyle(res.data.learning_style));
  }, []);

  useEffect(() => {
    if (style !== "kinesthetic") return;

    api.get("/practice/tasks").then((res) => {
      setTasks(res.data.tasks);
      const first = res.data.tasks[0] || null;
      setSelectedTask(first);
      setCode(first?.starter_code || "");
    });
    api.get("/practice/mine").then((res) => setActivities(res.data));
  }, [style]);

  useEffect(() => {
    if (style !== "kinesthetic") return;
    const id = setInterval(() => setTimeSpent((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, [style]);

  const onTaskChange = (taskName) => {
    const found = tasks.find((t) => t.task_name === taskName) || null;
    setSelectedTask(found);
    if (found) setCode(found.starter_code);
    setRunOutput({ stdout: "", stderr: "", status: "" });
  };

  const runCode = async () => {
    setLoading(true);
    try {
      const res = await api.post("/practice/run", {
        source_code: code,
      });
      setRunOutput({
        stdout: res.data.stdout || "",
        stderr: res.data.stderr || "",
        status: res.data.judge0_status || res.data.status || "",
      });
    } catch (err) {
      setRunOutput({
        stdout: "",
        stderr: err.response?.data?.error || "Run failed",
        status: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!selectedTask) return;
    await api.post("/practice/submit", {
      task_name: selectedTask.task_name,
      status: runOutput.stderr ? "needs_review" : "completed",
      code_submitted: code,
      time_spent: timeSpent,
    });
    setTimeSpent(0);
    const res = await api.get("/practice/mine");
    setActivities(res.data);
    alert("Practice activity saved");
  };

  if (style && style !== "kinesthetic") {
    return (
      <>
        <NavBar />
        <div className="container py-4">
          <div className="alert alert-warning mb-0">Virtual practice lab is available only for kinesthetic learners.</div>
        </div>
      </>
    );
  }

  return (
    <>
      <NavBar />
      <div className="container pb-5">
        <div className="glass-card p-4 mb-4">
          <h4>Virtual Practice Lab (Java)</h4>
          <p className="mb-2">Time spent: {timeSpent}s</p>

          <label className="form-label">Select Task</label>
          <select
            className="form-select mb-2"
            value={selectedTask?.task_name || ""}
            onChange={(e) => onTaskChange(e.target.value)}
          >
            {tasks.map((t) => (
              <option key={t.task_name} value={t.task_name}>
                {t.task_name}
              </option>
            ))}
          </select>

          {selectedTask?.description && <p className="text-muted">{selectedTask.description}</p>}

          <textarea className="form-control" rows={14} value={code} onChange={(e) => setCode(e.target.value)} />

          <div className="d-flex gap-2 mt-3">
            <button className="btn btn-outline-primary" onClick={runCode} disabled={loading}>
              {loading ? "Running..." : "Run Code"}
            </button>
            <button className="btn btn-warning" onClick={submit}>Submit Activity</button>
          </div>

          {(runOutput.stdout || runOutput.stderr || runOutput.status) && (
            <div className="mt-3 border rounded p-3 bg-light">
              <p className="mb-1"><strong>Status:</strong> {runOutput.status || "n/a"}</p>
              {runOutput.stdout && <pre className="mb-1" style={{ whiteSpace: "pre-wrap" }}>{runOutput.stdout}</pre>}
              {runOutput.stderr && <pre className="mb-0 text-danger" style={{ whiteSpace: "pre-wrap" }}>{runOutput.stderr}</pre>}
            </div>
          )}
        </div>

        <div className="glass-card p-4">
          <h5>Recent Activity</h5>
          {activities.length === 0 ? (
            <p className="text-muted mb-0">No activity yet.</p>
          ) : (
            <ul className="mb-0">
              {activities.map((a) => (
                <li key={a.activity_id}>{a.task_name} | {a.status} | {a.time_spent}s</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
