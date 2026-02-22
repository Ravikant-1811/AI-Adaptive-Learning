import { useEffect, useState } from "react";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function PracticePage() {
  const [style, setStyle] = useState(null);
  const [styleLoading, setStyleLoading] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [code, setCode] = useState("");
  const [timeSpent, setTimeSpent] = useState(0);
  const [activities, setActivities] = useState([]);
  const [runOutput, setRunOutput] = useState({ stdout: "", stderr: "", status: "", note: "", runner: "" });
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [pageLoading, setPageLoading] = useState(false);
  const [pageError, setPageError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [submitSuccess, setSubmitSuccess] = useState("");
  const [downloadError, setDownloadError] = useState("");
  const [taskSource, setTaskSource] = useState("default");
  const [taskTopic, setTaskTopic] = useState("");

  useEffect(() => {
    setStyleLoading(true);
    api
      .get("/style/mine")
      .then((res) => setStyle(res.data.learning_style))
      .catch(() => setStyle(null))
      .finally(() => setStyleLoading(false));
  }, []);

  useEffect(() => {
    if (style !== "kinesthetic") return;
    setPageLoading(true);
    setPageError("");
    Promise.all([api.get("/practice/tasks"), api.get("/practice/mine")])
      .then(([taskRes, activityRes]) => {
        const taskList = taskRes.data.tasks || [];
        setTasks(taskList);
        setTaskSource(taskRes.data.source || "default");
        setTaskTopic(taskRes.data.topic || "");
        const first = taskList[0] || null;
        setSelectedTask(first);
        setCode(first?.starter_code || "");
        setActivities(activityRes.data || []);
      })
      .catch((err) => {
        setPageError(err.response?.data?.error || "Failed to load practice lab.");
      })
      .finally(() => setPageLoading(false));
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
    setRunOutput({ stdout: "", stderr: "", status: "", note: "", runner: "" });
  };

  const runCode = async () => {
    if (!selectedTask) {
      setPageError("Please select a task before running code.");
      return;
    }
    setLoading(true);
    setPageError("");
    setSubmitSuccess("");
    try {
      const res = await api.post("/practice/run", {
        source_code: code,
      });
      setRunOutput({
        stdout: res.data.stdout || "",
        stderr: res.data.stderr || "",
        status: res.data.judge0_status || res.data.status || "",
        note: res.data.note || "",
        runner: res.data.runner || "",
      });
    } catch (err) {
      setPageError("");
      setRunOutput({
        stdout: "",
        stderr: err.response?.data?.error || "Run failed",
        status: "error",
        note: "",
        runner: "",
      });
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    setSubmitError("");
    setSubmitSuccess("");
    if (!selectedTask) {
      setSubmitError("Please select a task first.");
      return;
    }
    try {
      setSubmitting(true);
      await api.post("/practice/submit", {
        task_name: selectedTask.task_name,
        status: runOutput.stderr ? "needs_review" : "completed",
        code_submitted: code,
        time_spent: timeSpent,
      });
      setTimeSpent(0);
      const res = await api.get("/practice/mine");
      setActivities(res.data);
      setSubmitSuccess("Practice activity saved.");
    } catch (err) {
      setSubmitError(err.response?.data?.error || "Failed to save practice activity.");
    } finally {
      setSubmitting(false);
    }
  };

  const downloadPracticeAsset = async (contentType) => {
    if (!selectedTask) return;
    setDownloadError("");
    const content = [
      `Task: ${selectedTask.task_name}`,
      `Description: ${selectedTask.description || ""}`,
      "",
      "Current Code:",
      code || "",
      "",
      "Latest Run Output:",
      runOutput.stdout || runOutput.stderr || "No run output yet.",
    ].join("\n");

    try {
      const created = await api.post("/downloads/", {
        content_type: contentType,
        topic: selectedTask.task_name,
        content,
      });
      const fileResp = await api.get(`/downloads/file/${created.data.download_id}`, { responseType: "blob" });
      const blobUrl = window.URL.createObjectURL(new Blob([fileResp.data]));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `${selectedTask.task_name.replace(/\s+/g, "_")}_${contentType}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      setDownloadError(err.response?.data?.error || "Failed to download file.");
    }
  };

  if (styleLoading) {
    return (
      <>
        <NavBar />
        <div className="container py-4">
          <div className="alert alert-info mb-0">Loading practice lab...</div>
        </div>
      </>
    );
  }

  if (!style) {
    return (
      <>
        <NavBar />
        <div className="container py-4">
          <div className="alert alert-warning mb-0">Set your learning style first to access the practice lab.</div>
        </div>
      </>
    );
  }

  if (style !== "kinesthetic") {
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
          {pageError && <div className="alert alert-danger py-2">{pageError}</div>}
          {submitError && <div className="alert alert-danger py-2">{submitError}</div>}
          {submitSuccess && <div className="alert alert-success py-2">{submitSuccess}</div>}
          {pageLoading && <div className="alert alert-info py-2">Loading tasks and activity...</div>}
          <p className="mb-1 text-muted">
            Task Source: <strong>{taskSource === "ai" ? "AI from latest chatbot question" : "Default task bank"}</strong>
          </p>
          {taskTopic && <p className="mb-2 text-muted">Current Topic: <strong>{taskTopic}</strong></p>}

          <label className="form-label">Select Task</label>
          <select
            className="form-select mb-2"
            value={selectedTask?.task_name || ""}
            onChange={(e) => onTaskChange(e.target.value)}
            disabled={pageLoading || tasks.length === 0}
          >
            {tasks.length === 0 && <option value="">No tasks available</option>}
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
            <button className="btn btn-warning" onClick={submit} disabled={!selectedTask || submitting}>
              {submitting ? "Submitting..." : "Submit Activity"}
            </button>
            <button className="btn btn-outline-secondary" onClick={() => downloadPracticeAsset("task_sheet")}>
              Download Task
            </button>
            <button className="btn btn-outline-success" onClick={() => downloadPracticeAsset("solution")}>
              Download Solution
            </button>
          </div>
          {downloadError && <div className="alert alert-danger py-2 mt-2 mb-0">{downloadError}</div>}

          {(runOutput.stdout || runOutput.stderr || runOutput.status || loading) && (
            <div className="mt-3 border rounded p-3 bg-light">
              <p className="mb-1"><strong>Status:</strong> {loading ? "running" : (runOutput.status || "n/a")}</p>
              {runOutput.runner && <p className="mb-1"><strong>Runner:</strong> {runOutput.runner}</p>}
              {runOutput.note && <p className="mb-1 text-muted"><small>{runOutput.note}</small></p>}
              {loading && <p className="mb-1">Executing your Java program...</p>}
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
