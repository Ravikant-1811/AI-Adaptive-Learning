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
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed");
    }
  };

  return (
    <div className="container py-5" style={{ maxWidth: 520 }}>
      <div className="glass-card p-4">
        <h3 className="mb-3">Create Account</h3>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        <form onSubmit={submit} className="d-grid gap-3">
          <input className="form-control" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="form-control" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input type="password" className="form-control" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="btn brand-btn text-white">Register</button>
        </form>
        <p className="mt-3 mb-0">Already have an account? <Link to="/login">Login</Link></p>
      </div>
    </div>
  );
}
