"use client";

import { DeskStateSnapshot } from "@/lib/types";

function fmt(value?: number | null) {
  return value == null ? "—" : value.toFixed(2);
}

export function DeskStateHeader({
  desk,
  refreshing,
  onRefresh
}: {
  desk: DeskStateSnapshot;
  refreshing: boolean;
  onRefresh: () => void;
}) {
  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Always-On Intelligence</div>
          <h2>Desk observatory</h2>
        </div>
        <div className="button-row">
          <div className="muted">Snapshot {desk.snapshot_timestamp.slice(0, 19)}</div>
          <button className="button-secondary" onClick={onRefresh} disabled={refreshing}>
            {refreshing ? "Refreshing…" : "Refresh Desk"}
          </button>
        </div>
      </div>
      <div className="grid-4">
        <div className="metric">
          <div className="metric-label">Dominant Regime</div>
          <div className="metric-value">{desk.dominant_regime?.replaceAll("_", " ") ?? "Unknown"}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Coherence / Fragmentation</div>
          <div className="metric-value">
            {fmt(desk.coherence_score)} / {fmt(desk.fragmentation_score)}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Stress / Dispersion</div>
          <div className="metric-value">
            {fmt(desk.stress_score)} / {fmt(desk.state_dispersion)}
          </div>
        </div>
        <div className="metric">
          <div className="metric-label">Attention Pair</div>
          <div className="metric-value">{desk.attention_pair_id ?? "None"}</div>
        </div>
      </div>
      <div className="button-row" style={{ marginTop: 14 }}>
        <div className={`status-pill ${desk.freshness_status === "fresh" ? "status-success" : desk.freshness_status === "degraded" ? "status-error" : "status-idle"}`}>
          freshness {desk.freshness_status}
        </div>
        {desk.degraded ? <div className="status-pill status-error">degraded state</div> : null}
        {desk.refresh_status?.completed_at ? (
          <div className="muted">
            last refresh {desk.refresh_status.completed_at.slice(0, 19)} · ok {desk.refresh_status.success_count} · failed {desk.refresh_status.failed_count}
          </div>
        ) : null}
      </div>
      {desk.refresh_status?.warnings?.length ? (
        <div className="muted" style={{ marginTop: 10 }}>
          {desk.refresh_status.warnings.join(" · ")}
        </div>
      ) : null}
    </section>
  );
}
