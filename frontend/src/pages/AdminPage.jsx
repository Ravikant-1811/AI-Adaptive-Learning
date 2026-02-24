import { useEffect, useMemo, useState } from "react";
import NavBar from "../components/NavBar";
import api from "../services/api";

export default function AdminPage() {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  const loadData = async (search = "") => {
    setLoading(true);
    setError("");
    try {
      const [summaryRes, usersRes] = await Promise.all([
        api.get("/admin/summary"),
        api.get("/admin/users", { params: search ? { q: search } : {} }),
      ]);
      setSummary(summaryRes.data);
      setUsers(usersRes.data || []);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to load admin panel.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const metrics = useMemo(() => summary?.metrics || {}, [summary]);

  const onSearch = (e) => {
    e.preventDefault();
    loadData(query.trim());
  };

  const onDeleteUser = async (userId) => {
    const ok = window.confirm("Delete this user and all their records?");
    if (!ok) return;
    setActionMsg("");
    try {
      await api.delete(`/admin/users/${userId}`);
      setActionMsg(`Deleted user ${userId}`);
      await loadData(query.trim());
    } catch (err) {
      setError(err.response?.data?.error || "Failed to delete user.");
    }
  };

  return (
    <>
      <NavBar />
      <div className="container page-wrap">
        <header className="page-header">
          <p className="page-kicker mb-1">Administrator</p>
          <h2 className="page-title">Admin Control Panel</h2>
          <p className="page-subtitle">Manage users and monitor platform activity.</p>
        </header>

        {error && <div className="alert alert-danger py-2">{error}</div>}
        {actionMsg && <div className="alert alert-success py-2">{actionMsg}</div>}

        <div className="glass-card p-4 mb-4">
          <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
            <h5 className="mb-0">Platform Metrics</h5>
            <button className="btn surface-btn btn-sm" onClick={() => loadData(query.trim())} disabled={loading}>
              Refresh
            </button>
          </div>
          <div className="metric-grid">
            <article className="metric-card"><p className="metric-label">Users</p><div className="metric-value">{metrics.users || 0}</div></article>
            <article className="metric-card"><p className="metric-label">Styles Set</p><div className="metric-value">{metrics.learning_styles || 0}</div></article>
            <article className="metric-card"><p className="metric-label">Chat Messages</p><div className="metric-value">{metrics.chat_messages || 0}</div></article>
            <article className="metric-card"><p className="metric-label">Practice Submissions</p><div className="metric-value">{metrics.practice_submissions || 0}</div></article>
            <article className="metric-card"><p className="metric-label">Downloads</p><div className="metric-value">{metrics.downloads || 0}</div></article>
          </div>
        </div>

        <div className="glass-card p-4 mb-4">
          <form className="d-flex gap-2 mb-3" onSubmit={onSearch}>
            <input
              className="form-control"
              placeholder="Search by name or email"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="btn brand-btn" type="submit" disabled={loading}>Search</button>
          </form>

          <h5 className="mb-3">Users</h5>
          {loading ? (
            <p className="mb-0 text-muted">Loading...</p>
          ) : users.length === 0 ? (
            <p className="mb-0 text-muted">No users found.</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-sm align-middle">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Style</th>
                    <th>Stats</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.user_id}>
                      <td>{u.user_id}</td>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td>{u.learning_style || "not set"}</td>
                      <td>C:{u.stats?.chats || 0} D:{u.stats?.downloads || 0} P:{u.stats?.practice || 0}</td>
                      <td>
                        {!u.is_admin && (
                          <button className="btn btn-sm btn-danger" onClick={() => onDeleteUser(u.user_id)}>
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
