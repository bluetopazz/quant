"use client";

import { PairStateSnapshot } from "@/lib/types";

function fmt(value?: number | null) {
  return value == null ? "—" : value.toFixed(2);
}

export function PairStateMatrix({ states }: { states: PairStateSnapshot[] }) {
  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Pair States</div>
          <h3>State matrix</h3>
        </div>
      </div>
      <div className="state-matrix">
        {states.map((state) => (
          <article className="state-card" key={state.snapshot_id}>
            <div className="headline">
              <div>
                <div className="kicker">{state.pair_id}</div>
                <h3>{state.regime_label?.replaceAll("_", " ") ?? "Unknown regime"}</h3>
              </div>
              <div className={`status-pill ${state.staleness_status === "fresh" ? "status-success" : "status-idle"}`}>
                {state.staleness_status}
              </div>
            </div>
            <p className="muted" style={{ marginTop: 0 }}>{state.relationship}</p>
            <div className="metric-grid">
              <div className="metric">
                <div className="metric-label">z-score</div>
                <div className="metric-value">{fmt(state.signal_zscore)}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Velocity</div>
                <div className="metric-value">{fmt(state.signal_velocity_5d)}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Corr 90D</div>
                <div className="metric-value">{fmt(state.corr_90d)}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Vol Regime</div>
                <div className="metric-value">{state.vol_regime ?? "—"}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Primary Driver</div>
                <div className="metric-value">{state.driver_label ?? "—"}</div>
              </div>
              <div className="metric">
                <div className="metric-label">Attention</div>
                <div className="metric-value">{fmt(state.attention_score)}</div>
              </div>
            </div>
            <p className="muted" style={{ marginBottom: 0 }}>
              {state.directional_bias ?? "No directional bias"}{state.confidence ? ` · confidence ${state.confidence}` : ""}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
