"use client";

import { CouplingSnapshot } from "@/lib/types";

function cellStyle(value: number | null) {
  if (value == null) {
    return {};
  }
  const alpha = Math.min(0.85, Math.max(0.1, value));
  return {
    background: `rgba(138, 75, 20, ${alpha})`,
    color: value > 0.55 ? "#fff" : "#1f1b16"
  };
}

export function CouplingHeatmap({ coupling }: { coupling?: CouplingSnapshot | null }) {
  if (!coupling) {
    return (
      <section className="panel">
        <div className="kicker">Coupling</div>
        <h3>No coupling snapshot yet</h3>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Cross-Pair Coupling</div>
          <h3>State similarity matrix</h3>
        </div>
        <div className="muted">
          coherence {coupling.coherence_score?.toFixed(2) ?? "—"} · fragmentation {coupling.fragmentation_score?.toFixed(2) ?? "—"}
          {coupling.coherence_delta != null ? ` · Δ coherence ${coupling.coherence_delta >= 0 ? "+" : ""}${coupling.coherence_delta.toFixed(2)}` : ""}
        </div>
      </div>
      <div className="table-wrap">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th>Pair</th>
              {coupling.pair_ids.map((pairId) => (
                <th key={pairId}>{pairId}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {coupling.pair_ids.map((pairId, rowIdx) => (
              <tr key={pairId}>
                <td>{pairId}</td>
                {coupling.matrix[rowIdx]?.map((value, colIdx) => (
                  <td key={`${pairId}-${coupling.pair_ids[colIdx]}`} style={cellStyle(value)}>
                    {value == null ? "—" : value.toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
