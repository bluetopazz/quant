"use client";

import { useEffect, useState } from "react";

import { ProtectedPage } from "@/components/auth/ProtectedPage";
import { ChangeSummaryPanel } from "@/components/intelligence/ChangeSummaryPanel";
import { CouplingHeatmap } from "@/components/intelligence/CouplingHeatmap";
import { DeskStateHeader } from "@/components/intelligence/DeskStateHeader";
import { DeskSystemTrend } from "@/components/intelligence/DeskSystemTrend";
import { PairStateMatrix } from "@/components/intelligence/PairStateMatrix";
import { PairTrajectoryGrid } from "@/components/intelligence/PairTrajectoryGrid";
import { fetchIntelligenceOverview, refreshIntelligenceOverview } from "@/lib/api";
import { IntelligenceOverview } from "@/lib/types";

export default function IntelligencePage() {
  const [overview, setOverview] = useState<IntelligenceOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const runRefresh = async () => {
    setRefreshing(true);
    try {
      setOverview(await refreshIntelligenceOverview());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not refresh intelligence overview");
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchIntelligenceOverview()
      .then((data) => {
        setOverview(data);
        if (data.desk.freshness_status !== "fresh" || data.desk.coverage_ratio < 1) {
          void runRefresh();
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load intelligence overview"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedPage>
      <div className="headline" style={{ marginBottom: 18 }}>
        <div>
          <div className="kicker">System State</div>
          <h2>Always-on intelligence observatory</h2>
        </div>
      </div>
      {error ? <div className="panel" style={{ color: "var(--danger)" }}>{error}</div> : null}
      {loading ? <div className="panel">Loading intelligence state…</div> : null}
      {!loading && overview ? (
        <div className="card-stack">
          <DeskStateHeader desk={overview.desk} refreshing={refreshing} onRefresh={() => void runRefresh()} />
          <DeskSystemTrend history={overview.desk.desk_history} />
          <PairStateMatrix states={overview.desk.pair_states} />
          <PairTrajectoryGrid trajectories={overview.trajectories} />
          <CouplingHeatmap coupling={overview.desk.coupling} />
          <ChangeSummaryPanel changes={overview.desk.change_summaries} flags={overview.desk.attention_flags} />
        </div>
      ) : null}
    </ProtectedPage>
  );
}
