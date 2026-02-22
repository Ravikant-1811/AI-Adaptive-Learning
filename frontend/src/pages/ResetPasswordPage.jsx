import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [generatedToken, setGeneratedToken] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const requestToken = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setGeneratedToken("");
    try {
      const res = await api.post("/auth/forgot-password", { email });
      setMessage(res.data.message || "Reset token generated.");
      if (res.data.reset_token) setGeneratedToken(res.data.reset_token);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to generate reset token.");
    }
  };

  const resetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      const res = await api.post("/auth/reset-password", {
        token,
        new_password: newPassword,
      });
      setMessage(res.data.message || "Password reset successful.");
      setToken("");
      setNewPassword("");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to reset password.");
    }
  };

  return (
    <div className="container py-5" style={{ maxWidth: 560 }}>
      <div className="glass-card p-4 mb-3">
        <h3 className="mb-3">Forgot Password</h3>
        {error && <div className="alert alert-danger py-2">{error}</div>}
        {message && <div className="alert alert-success py-2">{message}</div>}
        <form onSubmit={requestToken} className="d-grid gap-3">
          <input
            className="form-control"
            placeholder="Registered email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button className="btn btn-outline-primary">Generate Reset Token</button>
        </form>
        {generatedToken && (
          <div className="alert alert-warning py-2 mt-3 mb-0">
            Demo reset token: <code>{generatedToken}</code>
          </div>
        )}
      </div>

      <div className="glass-card p-4">
        <h3 className="mb-3">Reset Password</h3>
        <form onSubmit={resetPassword} className="d-grid gap-3">
          <input
            className="form-control"
            placeholder="Reset token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
          <input
            type="password"
            className="form-control"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <button className="btn brand-btn text-white">Reset Password</button>
        </form>
        <p className="mt-3 mb-0">
          Back to <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
