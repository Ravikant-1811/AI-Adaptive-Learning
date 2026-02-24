import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function PracticePage() {
  const [searchParams] = useSearchParams();
  const linkedTopicParam = (searchParams.get("topic") || "").trim();
  const linkedTaskParam = (searchParams.get("task") || "").trim();

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
  const [topicCatalog, setTopicCatalog] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [usingLinkedBundle, setUsingLinkedBundle] = useState(false);

  const normalizeTopic = (value) =>
    (value || "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const mapChatTaskToPracticeTask = (task) => ({
    task_name: task.task_name,
    description: task.description || "Task assigned from chat.",
    starter_code:
      task.starter_code ||
      "public class Main {\n  public static void main(String[] args) {\n    // Implement this task\n  }\n}",
  });

  const loadFromLinkedBundle = (topic, preferredTaskName = "") => {
    const raw = localStorage.getItem("linkedPracticeBundle");
    if (!raw) return false;
    try {
      const parsed = JSON.parse(raw);
      if (!parsed?.topic || !Array.isArray(parsed?.tasks) || parsed.tasks.length === 0) return false;
      if (topic && normalizeTopic(parsed.topic) !== normalizeTopic(topic)) return false;

      const taskList = parsed.tasks.map(mapChatTaskToPracticeTask);
      if (taskList.length === 0) return false;
      setTasks(taskList);
      setTaskSource("chat-assigned");
      setTaskTopic(parsed.topic);
      setUsingLinkedBundle(true);

      const preferredTask = preferredTaskName
        ? taskList.find((t) => t.task_name.toLowerCase() === preferredTaskName.toLowerCase())
        : null;
      const selected = preferredTask || taskList[0] || null;
      setSelectedTask(selected);
      setCode(selected?.starter_code || "");
      return true;
    } catch {
      localStorage.removeItem("linkedPracticeBundle");
      return false;
    }
  };

  const loadTasksByTopic = async (topic, preferredTaskName = "", forceApi = false) => {
    if (topic && loadFromLinkedBundle(topic, preferredTaskName)) return;
    if (!topic && !forceApi && loadFromLinkedBundle("", preferredTaskName)) return;

    const query = topic ? `?topic=${encodeURIComponent(topic)}` : "";
    let taskRes;
    try {
      taskRes = await api.get(`/practice/tasks${query}`);
    } catch (err) {
      if (!forceApi && loadFromLinkedBundle("", preferredTaskName)) return;
      throw err;
    }
    const taskList = taskRes.data.tasks || [];

    setUsingLinkedBundle(false);
    setTasks(taskList);
    setTaskSource(taskRes.data.source || "default");
    setTaskTopic(taskRes.data.topic || topic || "");

    const preferredTask = preferredTaskName
      ? taskList.find((t) => t.task_name.toLowerCase() === preferredTaskName.toLowerCase())
      : null;
    const selected = preferredTask || taskList[0] || null;
    setSelectedTask(selected);
    setCode(selected?.starter_code || "");
  };

  const loadPracticeData = async () => {
    if (style !== "kinesthetic") return;
    setPageLoading(true);
    setPageError("");
    try {
      const [topicRes, activityRes] = await Promise.allSettled([api.get("/practice/topics"), api.get("/practice/mine")]);
      const catalog = [...(topicRes.status === "fulfilled" ? topicRes.value.data.topics || [] : [])];

      if (linkedTopicParam && !catalog.some((t) => t.topic === linkedTopicParam)) {
        catalog.unshift({ topic: linkedTopicParam, tasks: [] });
      }
      setTopicCatalog(catalog);

      const bundleRaw = localStorage.getItem("linkedPracticeBundle");
      let bundleTopic = "";
      if (bundleRaw) {
        try {
          const parsed = JSON.parse(bundleRaw);
          bundleTopic = parsed?.topic || "";
        } catch {
          bundleTopic = "";
        }
      }

      const targetTopic = linkedTopicParam || bundleTopic || catalog[0]?.topic || "";
      if (targetTopic) {
        setSelectedTopic(targetTopic);
        await loadTasksByTopic(targetTopic, linkedTaskParam);
      } else {
        await loadTasksByTopic("", linkedTaskParam);
      }

      if (activityRes.status === "fulfilled") {
        setActivities(activityRes.value.data || []);
      } else {
        setActivities([]);
      }

      if (topicRes.status === "rejected") setPageError("Topics list unavailable, but task runner is ready.");
    } catch (err) {
      setPageError(err.response?.data?.error || "Failed to load practice lab.");
    } finally {
      setPageLoading(false);
    }
  };

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
    loadPracticeData();
  }, [style, linkedTopicParam, linkedTaskParam]);

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
      const res = await api.post("/practice/run", { source_code: code });
      setRunOutput({
        stdout: res.data.stdout || "",
        stderr: res.data.stderr || "",
        status: res.data.judge0_status || res.data.status || "",
        note: res.data.note || "",
        runner: res.data.runner || "",
      });
    } catch (err) {
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
      setActivities(res.data || []);
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
      <div className="container page-wrap">
        <header className="page-header">
          <p className="page-kicker mb-1">Hands-on Workspace</p>
          <h2 className="page-title">Virtual Java Practice Lab</h2>
          <p className="page-subtitle">Run, submit, and track coding tasks synced from chatbot learning topics.</p>
        </header>

        <div className="glass-card p-4 mb-4">
          <h4>Interactive Task Runner</h4>
          {linkedTopicParam && (
            <div className="alert alert-primary py-2">
              Synced from chat topic: <strong>{linkedTopicParam}</strong>
              {linkedTaskParam && <> | Task: <strong>{linkedTaskParam}</strong></>}
              {usingLinkedBundle && <> | Using exact chat-assigned tasks</>}
            </div>
          )}

          <p className="mb-2">Time spent: {timeSpent}s</p>
          {pageError && <div className="alert alert-danger py-2">{pageError}</div>}
          {submitError && <div className="alert alert-danger py-2">{submitError}</div>}
          {submitSuccess && <div className="alert alert-success py-2">{submitSuccess}</div>}
          {pageLoading && <div className="alert alert-info py-2">Loading tasks and activity...</div>}

          <p className="mb-1 text-muted">
            Task Source: <strong>{
              taskSource === "chat-assigned"
                ? "Directly assigned from chat"
                : taskSource === "ai"
                  ? "AI generated"
                  : taskSource === "catalog"
                    ? "Topic catalog"
                    : "Default task bank"
            }</strong>
          </p>
          {taskTopic && <p className="mb-2 text-muted">Current Topic: <strong>{taskTopic}</strong></p>}
          <p className="mb-2 text-muted">Tasks Loaded: <strong>{tasks.length}</strong></p>

          <div className="d-flex gap-2 mb-3">
            <select
              className="form-select"
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              disabled={pageLoading || topicCatalog.length === 0}
            >
              {topicCatalog.map((item) => (
                <option key={item.topic} value={item.topic}>
                  {item.topic}
                </option>
              ))}
            </select>
            <button
              className="btn surface-btn"
              disabled={pageLoading || !selectedTopic}
              onClick={async () => {
                setPageLoading(true);
                setPageError("");
                try {
                  await loadTasksByTopic(selectedTopic);
                } catch (err) {
                  setPageError(err.response?.data?.error || "Failed to load selected topic tasks.");
                } finally {
                  setPageLoading(false);
                }
              }}
            >
              Load Topic Tasks
            </button>
          </div>

          <button className="btn btn-sm btn-outline-dark mb-3" onClick={loadPracticeData} disabled={pageLoading}>
            {pageLoading ? "Refreshing..." : "Refresh Tasks"}
          </button>

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
            <button className="btn surface-btn" onClick={() => downloadPracticeAsset("task_sheet")}>
              Download Task
            </button>
            <button className="btn surface-btn" onClick={() => downloadPracticeAsset("solution")}>
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
          <h5 className="mb-3">All Topics and Tasks</h5>
          {topicCatalog.length === 0 ? (
            <p className="text-muted">No topics available.</p>
          ) : (
            <div className="d-grid gap-3 mb-4">
              {topicCatalog.map((topicItem) => (
                <div key={topicItem.topic} className="border rounded p-3">
                  <h6 className="mb-2">{topicItem.topic}</h6>
                  <ul className="mb-0">
                    {(topicItem.tasks || []).map((task) => (
                      <li key={`${topicItem.topic}-${task.task_name}`}>
                        <strong>{task.task_name}</strong>: {task.description}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

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
