"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { DeskHistoryPoint } from "@/lib/types";

export function DeskSystemTrend({ history }: { history: DeskHistoryPoint[] }) {
  return (
    <section className="panel">
      <div className="headline" style={{ marginBottom: 14 }}>
        <div>
          <div className="kicker">Desk Dynamics</div>
          <h3>Coherence and stress through recent snapshots</h3>
        </div>
      </div>
      {!history.length ? (
        <p className="muted">No desk snapshot history yet.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="snapshot_timestamp" tickFormatter={(value) => String(value).slice(5, 10)} />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => String(value).slice(0, 19)}
              contentStyle={{ background: "#fffdf9", border: "1px solid #d2c1ab" }}
            />
            <Legend />
            <Line type="monotone" dataKey="coherence_score" stroke="#2e6b46" dot={false} name="Coherence" />
            <Line type="monotone" dataKey="fragmentation_score" stroke="#8f2e2e" dot={false} name="Fragmentation" />
            <Line type="monotone" dataKey="stress_score" stroke="#8a4b14" dot={false} name="Stress" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}
