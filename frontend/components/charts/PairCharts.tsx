"use client";

import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartPayload } from "@/lib/types";

function toRows(payload: ChartPayload) {
  return payload.x_axis.values.map((label, index) => {
    const row: Record<string, string | number | null> = { x: label };
    for (const series of payload.series) {
      row[series.label] = series.values[index] ?? null;
    }
    return row;
  });
}

function ChartBlock({ chart }: { chart: ChartPayload }) {
  const rows = toRows(chart);
  if (!rows.length || !chart.series.length) {
    return <div className="empty-state">No chart payload available yet.</div>;
  }

  return (
    <div className="panel chart-panel">
      <div className="headline">
        <h3>{chart.title}</h3>
      </div>
      <ResponsiveContainer width="100%" height={240}>
        {chart.render_kind === "bar" ? (
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" hide />
            <YAxis />
            <Tooltip />
            <Legend />
            {chart.series.map((series, index) => (
              <Bar key={series.series_id} dataKey={series.label} fill={index % 2 === 0 ? "#8a4b14" : "#1f1b16"} />
            ))}
          </BarChart>
        ) : (
          <LineChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="x" hide />
            <YAxis />
            <Tooltip />
            <Legend />
            {chart.series.map((series, index) => (
              <Line
                key={series.series_id}
                type="monotone"
                dataKey={series.label}
                stroke={index % 2 === 0 ? "#8a4b14" : "#1f1b16"}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function PairCharts({ charts }: { charts?: ChartPayload[] }) {
  if (!charts?.length) {
    return <div className="empty-state">No chart payloads available yet.</div>;
  }

  return (
    <div className="grid-2">
      {charts.map((chart) => (
        <ChartBlock key={chart.chart_id} chart={chart} />
      ))}
    </div>
  );
}
