import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="container py-5">Loading...</div>;
  if (!user) return <Navigate to="/user-login" replace />;
  if (adminOnly && !user.is_admin) return <Navigate to="/dashboard" replace />;

  return children;
}
