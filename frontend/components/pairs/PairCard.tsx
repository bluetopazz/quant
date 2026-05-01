import Link from "next/link";

import { StatusPill } from "@/components/ui/StatusPill";
import { PairCard as PairCardType } from "@/lib/types";

export function PairCard({ pair }: { pair: PairCardType }) {
  return (
    <article className="panel pair-card">
      <div className="headline">
        <div>
          <div className="kicker">{pair.pair_id}</div>
          <h3>{pair.theme.replaceAll("_", " ")}</h3>
        </div>
        <StatusPill status={pair.latest_run?.status ?? "idle"} />
      </div>
      <p className="muted" style={{ margin: 0 }}>
        {pair.relationship}
      </p>
      <div className="metric-grid">
        <div className="metric">
          <div className="metric-label">Signal Shape</div>
          <div className="metric-value">{pair.signal_shape}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Prompt Style</div>
          <div className="metric-value">{pair.prompt_style}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Last Run</div>
          <div className="metric-value">{pair.latest_run?.run_timestamp?.slice(0, 19) ?? "Not yet run"}</div>
        </div>
      </div>
      <div className="button-row">
        <Link href={`/pairs/${pair.pair_id}`} className="button-primary">
          Open Pair
        </Link>
      </div>
    </article>
  );
}
