"use client";

import {
  Cell,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { PairTrajectoryPoint } from "@/lib/types";

function regimeColor(regime?: string | null) {
  if (!regime) return "#8a4b14";
  if (regime.includes("fragment")) return "#8f2e2e";
  if (regime.includes("stress") || regime.includes("distrust")) return "#c06a1a";
  if (regime.includes("alignment") || regime.includes("balance")) return "#2e6b46";
  return "#8a4b14";
}

export function PairTrajectoryGrid({ trajectories }: { trajectories: Record<string, PairTrajectoryPoint[]> }) {
  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Trajectories</div>
          <h3>State-space motion</h3>
        </div>
      </div>
      <div className="grid-2">
        {Object.entries(trajectories).map(([pairId, points]) => (
          <div className="chart-panel panel" key={pairId} style={{ minHeight: 320 }}>
            <div className="kicker">{pairId}</div>
            <h3 style={{ marginTop: 0 }}>{points[0]?.x_label ?? "State X"} vs {points[0]?.y_label ?? "State Y"}</h3>
            {!points.length ? (
              <p className="muted">No trajectory history yet.</p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={240}>
                <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" dataKey="x_value" name={points[0]?.x_label ?? "x"} />
                  <YAxis type="number" dataKey="y_value" name={points[0]?.y_label ?? "y"} />
                  <Tooltip
                    formatter={(value: number | string | Array<number | string>) => value}
                    labelFormatter={() => pairId}
                    contentStyle={{ background: "#fffdf9", border: "1px solid #d2c1ab" }}
                  />
                  <Scatter data={points} fill="#8a4b14" line={{ stroke: "#b78862", strokeDasharray: "4 3" }}>
                    {points.map((point) => (
                      <Cell key={point.run_id} fill={regimeColor(point.regime_label)} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
                <div className="muted" style={{ marginTop: 8 }}>
                  Current: {points[points.length - 1]?.region_label ?? "—"} · motion {points[points.length - 1]?.motion_label ?? "—"}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
