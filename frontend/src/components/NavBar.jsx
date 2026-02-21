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
    <nav className="navbar navbar-expand-lg bg-white border-bottom mb-4">
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/dashboard">
          Adaptive Learning
        </Link>
        <div className="navbar-nav ms-auto gap-2">
          <Link className="nav-link" to="/dashboard">Dashboard</Link>
          <Link className="nav-link" to="/chat">Chatbot</Link>
          <Link className="nav-link" to="/practice">Practice</Link>
          <button className="btn btn-outline-danger btn-sm" onClick={onLogout}>Logout</button>
        </div>
      </div>
    </nav>
  );
}
