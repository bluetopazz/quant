"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { saveSession } from "@/lib/auth";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("operator");
  const [password, setPassword] = useState("change-me");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const session = await login(username, password);
      saveSession(session);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page-shell">
      <form className="form-card panel" onSubmit={onSubmit}>
        <div className="kicker">Operator Login</div>
        <h1 style={{ marginTop: 0 }}>Enter the intelligence desk</h1>
        <p className="muted">Use the seeded operator credentials first, then change the backend defaults for real deployment.</p>
        <div className="field">
          <label htmlFor="username">Username</label>
          <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        {error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
        <button className="button-primary" type="submit" disabled={submitting}>
          {submitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}
