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
      await login(email, password);
      const style = await api.get("/style/mine");
      navigate(style.data.learning_style ? "/dashboard" : "/style");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed");
    }
  };

  return (
    <div className="container py-5" style={{ maxWidth: 520 }}>
      <div className="glass-card p-4">
        <h3 className="mb-3">Login</h3>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <form onSubmit={submit} className="d-grid gap-3">
          <input className="form-control" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input type="password" className="form-control" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="btn brand-btn text-white">Login</button>
        </form>
        <p className="mt-3 mb-0">No account? <Link to="/register">Register</Link></p>
      </div>
    </div>
  );
}
