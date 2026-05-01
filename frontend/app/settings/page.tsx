"use client";

import { useEffect, useState } from "react";

import { ProtectedPage } from "@/components/auth/ProtectedPage";
import { fetchHealth } from "@/lib/api";

export default function SettingsPage() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch((err) => setError(err instanceof Error ? err.message : "Could not load status"));
  }, []);

  return (
    <ProtectedPage>
      <div className="headline" style={{ marginBottom: 18 }}>
        <div>
          <div className="kicker">System</div>
          <h2>Runtime status</h2>
        </div>
      </div>
      {error ? <div className="panel" style={{ color: "var(--danger)" }}>{error}</div> : null}
      <div className="panel">
        <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>{JSON.stringify(health, null, 2)}</pre>
      </div>
    </ProtectedPage>
  );
}
