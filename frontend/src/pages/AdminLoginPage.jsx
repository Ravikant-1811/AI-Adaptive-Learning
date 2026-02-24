import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function AdminLoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password, "admin");
      navigate("/admin");
    } catch (err) {
      setError(err.response?.data?.error || "Admin login failed");
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-grid">
        <section className="auth-panel">
          <p className="page-kicker text-white-50 mb-2">Administrator Access</p>
          <h2 className="mb-2">Admin Control Login</h2>
          <p className="mb-0 text-white-50">
            Secure admin zone for monitoring users, chats, downloads, and platform activity.
          </p>
          <div className="auth-list">
            <div>Platform metrics and health overview</div>
            <div>User management controls</div>
            <div>Role-based protected route</div>
          </div>
        </section>

        <section className="glass-card auth-form">
          <h3 className="mb-1">Admin Login</h3>
          <p className="text-muted mb-3">Only emails in ADMIN_EMAILS are allowed.</p>
          {error && <div className="alert alert-danger py-2">{error}</div>}
          <form onSubmit={submit} className="d-grid gap-3">
            <input className="form-control" placeholder="Admin email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="password" className="form-control" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button className="btn brand-btn">Login as Admin</button>
          </form>
          <p className="mt-3 mb-0">Learner account? <Link to="/login">User Login</Link></p>
        </section>
      </div>
    </div>
  );
}
