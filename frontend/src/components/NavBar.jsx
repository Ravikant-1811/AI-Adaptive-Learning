import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function NavBar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg app-nav mb-4">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center gap-2" to="/dashboard">
          <span className="brand-mark">AL</span>
          <span className="brand-name">Adaptive Learning</span>
        </Link>

        <div className="navbar-nav ms-auto gap-2 align-items-center">
          <Link className="nav-link nav-pill" to="/dashboard">Dashboard</Link>
          <Link className="nav-link nav-pill" to="/chat">AI Chat</Link>
          <Link className="nav-link nav-pill" to="/practice">Practice</Link>
          <button className="btn btn-sm surface-btn" onClick={onLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}
