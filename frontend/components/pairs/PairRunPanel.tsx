import { StatusPill } from "@/components/ui/StatusPill";
import { PairRunResult } from "@/lib/types";

function renderMetrics(values: Record<string, unknown>) {
  const entries = Object.entries(values).filter(([, value]) => value !== null && value !== undefined);
  if (!entries.length) {
    return <div className="empty-state">No values available.</div>;
  }
  return (
    <div className="metric-grid">
      {entries.map(([key, value]) => (
          <div className="metric" key={key}>
            <div className="metric-label">{key}</div>
          <div className="metric-value">
            {typeof value === "object" ? JSON.stringify(value) : String(value)}
          </div>
        </div>
      ))}
    </div>
  );
}

export function PairRunPanel({ run }: { run: PairRunResult | null }) {
  if (!run) {
    return <div className="empty-state">No platform run recorded yet. Trigger a pair analysis to populate this panel.</div>;
  }

  return (
    <div className="card-stack">
      <div className="panel">
        <div className="headline">
          <div>
            <div className="kicker">Latest Run</div>
            <h3 style={{ marginTop: 0 }}>{run.run_timestamp?.slice(0, 19) ?? "Unknown time"}</h3>
          </div>
          <StatusPill status={run.status} />
        </div>
        {run.error ? <p style={{ color: "var(--danger)" }}>{run.error.message}</p> : null}
        {run.warnings?.length ? (
          <div>
            <div className="metric-label">Warnings</div>
            <ul>
              {run.warnings.map((warning) => (
                <li key={`${warning.warning_code}-${warning.message}`}>{warning.message}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>

      <div className="panel">
        <div className="kicker">Current State</div>
        {renderMetrics({
          ...run.feature_snapshot.core_metrics,
          ...run.feature_snapshot.pair_extensions
        })}
      </div>

      <div className="grid-2">
        <div className="panel">
          <div className="kicker">Parsed Signal</div>
          {renderMetrics((run.parsed_signal ?? {}) as Record<string, unknown>)}
        </div>
        <div className="panel">
          <div className="kicker">Sizing</div>
          {renderMetrics((run.risk_ticket ?? {}) as Record<string, unknown>)}
        </div>
      </div>

      <div className="panel">
        <div className="kicker">Journal Preview</div>
        {run.journal_entry_preview ? renderMetrics(run.journal_entry_preview.preview_payload) : <div className="empty-state">No journal preview available.</div>}
      </div>
    </div>
  );
}
