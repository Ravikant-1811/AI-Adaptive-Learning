import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await register(form.name, form.email, form.password);
      navigate("/user-login");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-grid">
        <section className="auth-panel">
          <p className="page-kicker text-white-50 mb-2">Get Started</p>
          <h2 className="mb-2">Create Your Adaptive Workspace</h2>
          <p className="mb-0 text-white-50">
            Register once and get a learning path customized to your cognitive style and live progress.
          </p>
          <div className="auth-list">
            <div>Secure JWT authentication with hashed passwords</div>
            <div>AI-driven style assessment and personalization</div>
            <div>Chat + task + downloads synced in one account</div>
          </div>
        </section>

        <section className="glass-card auth-form">
          <h3 className="mb-1">Create Account</h3>
          <p className="text-muted mb-3">Start your adaptive learning setup.</p>
          {error && <div className="alert alert-danger py-2">{error}</div>}
          <form onSubmit={submit} className="d-grid gap-3">
            <input className="form-control" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <input className="form-control" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input type="password" className="form-control" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
            <button className="btn brand-btn">Create account</button>
          </form>
          <p className="mt-3 mb-0">Already have an account? <Link to="/user-login">User Login</Link></p>
        </section>
      </div>
    </div>
  );
}
