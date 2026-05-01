import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page-shell">
      <div className="form-card panel">
        <div className="kicker">Macro Relative-Value Intelligence Suite</div>
        <h1 style={{ marginTop: 0 }}>Operator desk, now exposed as a platform</h1>
        <p className="muted">
          The notebooks remain the analytical reference path. This frontend is the operator interface on top of the
          FastAPI + <code>macro_intel</code> backend.
        </p>
        <div className="button-row">
          <Link href="/login" className="button-primary">
            Login
          </Link>
          <Link href="/dashboard" className="button-secondary">
            Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
