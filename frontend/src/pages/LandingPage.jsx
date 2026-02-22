import { Link } from "react-router-dom";

export default function LandingPage() {
  return (
    <div className="auth-shell">
      <div className="auth-grid">
        <section className="auth-panel">
          <p className="page-kicker text-white-50 mb-2">Adaptive AI Learning Platform</p>
          <h1 className="mb-2">One Platform. Three Learning Styles. Infinite Progress.</h1>
          <p className="mb-3 text-white-50">
            Analyze learner style, explain concepts with AI, assign synced tasks, and track outcomes in one workspace.
          </p>
          <div className="auth-list">
            <div>Psychological style test and direct selection</div>
            <div>Style-adaptive chatbot with downloadable assets</div>
            <div>Topic-linked Java practice lab with activity tracking</div>
          </div>
        </section>

        <section className="glass-card auth-form">
          <h3 className="mb-2">Start Learning Smarter</h3>
          <p className="text-muted mb-3">Choose an option to continue.</p>
          <div className="d-grid gap-2">
            <Link to="/register" className="btn brand-btn">Create Account</Link>
            <Link to="/login" className="btn surface-btn">Login</Link>
          </div>
        </section>
      </div>
    </div>
  );
}
