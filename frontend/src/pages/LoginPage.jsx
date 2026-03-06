import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import api from "../services/api";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password, "user");
      const style = await api.get("/style/mine");
      navigate(style.data.learning_style ? "/dashboard" : "/style");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-grid">
        <section className="auth-panel">
          <p className="page-kicker text-white-50 mb-2">AI Adaptive Platform</p>
          <h2 className="mb-2">Learn Your Way</h2>
          <p className="mb-0 text-white-50">
            Personalized chatbot, learning-style detection, and synced Java practice in one workflow.
          </p>
          <div className="auth-list">
            <div>Adaptive responses for Visual, Auditory, Kinesthetic</div>
            <div>Topic-based practice lab linked from chat</div>
            <div>Auto-generated downloadable learning resources</div>
          </div>
        </section>

        <section className="glass-card auth-form">
          <h3 className="mb-1">User Login</h3>
          <p className="text-muted mb-3">Login as learner to continue your personalized journey.</p>
          {error && <div className="alert alert-danger py-2">{error}</div>}
          <form onSubmit={submit} className="d-grid gap-3">
            <input className="form-control" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input type="password" className="form-control" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <button className="btn brand-btn">Login as User</button>
          </form>
          <div className="auth-actions mt-3">
            <p className="auth-actions-title mb-2">No account yet?</p>
            <Link to="/register" className="btn surface-btn w-100 mb-2">Create Account</Link>
            <div className="auth-links-row">
              <Link to="/admin-login" className="auth-link-pill">Admin Login</Link>
              <Link to="/reset-password" className="auth-link-pill">Forgot Password</Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
