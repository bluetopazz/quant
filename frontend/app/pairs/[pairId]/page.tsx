"use client";

import { use, useMemo, useState } from "react";

import { ProtectedPage } from "@/components/auth/ProtectedPage";
import { PairCharts } from "@/components/charts/PairCharts";
import { JournalTable } from "@/components/journal/JournalTable";
import { PairRunPanel } from "@/components/pairs/PairRunPanel";
import { useJournal } from "@/hooks/useJournal";
import { usePair } from "@/hooks/usePair";
import { useRunPair } from "@/hooks/useRunPair";

export default function PairPage({ params }: { params: Promise<{ pairId: string }> }) {
  const resolvedParams = use(params);
  const pairId = useMemo(() => decodeURIComponent(resolvedParams.pairId), [resolvedParams.pairId]);
  const { detail, latest, history, loading, error, refresh, setLatest } = usePair(pairId);
  const { entries, refresh: refreshJournal } = useJournal(pairId);
  const { execute, running, error: runError } = useRunPair(pairId, (result) => {
    setLatest(result);
    void refresh();
  });
  const [journalMessage, setJournalMessage] = useState<string | null>(null);

  const journalCurrentRun = async () => {
    if (!latest?.run_id) {
      return;
    }
    try {
      const { appendJournal } = await import("@/lib/api");
      await appendJournal(pairId, latest.run_id);
      await refreshJournal();
      setJournalMessage("Journal entry appended.");
    } catch (err) {
      setJournalMessage(err instanceof Error ? err.message : "Could not append journal entry");
    }
  };

  return (
    <ProtectedPage>
      {loading ? (
        <div className="panel">Loading pair...</div>
      ) : (
        <div className="card-stack">
          <div className="panel">
            <div className="headline">
              <div>
                <div className="kicker">{detail?.pair_id ?? pairId}</div>
                <h2 style={{ marginTop: 0 }}>{detail?.theme.replaceAll("_", " ") ?? "Pair Detail"}</h2>
              </div>
              <div className="button-row">
                <button className="button-primary" onClick={() => void execute()} disabled={running}>
                  {running ? "Running..." : "Run Analysis"}
                </button>
                <button className="button-secondary" onClick={() => void refresh()}>
                  Refresh View
                </button>
                <button className="button-secondary" onClick={() => void journalCurrentRun()} disabled={!latest?.run_id}>
                  Journal Current Idea
                </button>
              </div>
            </div>
            <p className="muted" style={{ marginBottom: 0 }}>
              {detail?.relationship}
            </p>
            {error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
            {runError ? <p style={{ color: "var(--danger)" }}>{runError}</p> : null}
            {journalMessage ? <p className="muted">{journalMessage}</p> : null}
          </div>

          <div className="grid-4">
            <div className="metric">
              <div className="metric-label">Prompt Style</div>
              <div className="metric-value">{detail?.prompt_style ?? "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">Parser Style</div>
              <div className="metric-value">{detail?.parser_style ?? "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">Signal Shape</div>
              <div className="metric-value">{detail?.signal_shape ?? "-"}</div>
            </div>
            <div className="metric">
              <div className="metric-label">History Count</div>
              <div className="metric-value">{history.length}</div>
            </div>
          </div>

          <PairRunPanel run={latest} />

          <div className="panel">
            <div className="kicker">Analyst Memo</div>
            <div className="memo-box">{latest?.analyst_memo?.content ?? "Run analysis to generate the memo."}</div>
          </div>

          <PairCharts charts={latest?.charts} />

          <div className="panel">
            <div className="headline" style={{ marginBottom: 12 }}>
              <h3>Recent Platform Runs</h3>
            </div>
            {!history.length ? (
              <div className="empty-state">No recent platform runs yet.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Run</th>
                    <th>Status</th>
                    <th>Timestamp</th>
                    <th>Warnings</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr key={item.run_id}>
                      <td>{item.run_id.slice(0, 12)}</td>
                      <td>{item.status}</td>
                      <td>{item.run_timestamp.slice(0, 19)}</td>
                      <td>{item.warning_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <JournalTable entries={entries} />
        </div>
      )}
    </ProtectedPage>
  );
}
