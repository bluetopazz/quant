"use client";

import { AttentionFlag, ChangeSummary } from "@/lib/types";

function fmt(value?: number | null) {
  return value == null ? "—" : value.toFixed(2);
}

export function ChangeSummaryPanel({
  changes,
  flags
}: {
  changes: ChangeSummary[];
  flags: AttentionFlag[];
}) {
  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Change Monitor</div>
          <h3>What changed and what matters</h3>
        </div>
      </div>
      <div className="grid-2">
        <div>
          <h4 style={{ marginTop: 0 }}>Recent changes</h4>
          <div className="card-stack">
            {changes.length ? changes.map((change) => (
              <article key={`${change.pair_id}-${change.changed_at ?? change.title}`} className="metric">
                <div className="metric-label">{change.pair_id}</div>
                <div className="metric-value" style={{ fontSize: "0.95rem" }}>{change.title}</div>
                <div className="muted">{change.description}</div>
                <div className="muted">
                  |z| Δ {fmt(change.absolute_zscore_change)} · vel Δ {fmt(change.velocity_change)} · corr Δ {fmt(change.corr_90d_change)}
                </div>
              </article>
            )) : <p className="muted">No change history yet.</p>}
          </div>
        </div>
        <div>
          <h4 style={{ marginTop: 0 }}>Attention flags</h4>
          <div className="card-stack">
            {flags.length ? flags.map((flag) => (
              <article key={`${flag.pair_id}-${flag.title}`} className="metric">
                <div className="metric-label">{flag.severity.toUpperCase()}</div>
                <div className="metric-value" style={{ fontSize: "0.95rem" }}>{flag.title}</div>
                <div className="muted">{flag.reason}</div>
                {flag.pair_ids?.length ? <div className="muted">pairs: {flag.pair_ids.join(", ")}</div> : null}
              </article>
            )) : <p className="muted">No active flags.</p>}
          </div>
        </div>
      </div>
    </section>
  );
}
