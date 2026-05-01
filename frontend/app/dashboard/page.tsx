"use client";

import { useEffect, useState } from "react";

import { ProtectedPage } from "@/components/auth/ProtectedPage";
import { PairCard } from "@/components/pairs/PairCard";
import { fetchPairs } from "@/lib/api";
import { PairCard as PairCardType } from "@/lib/types";

export default function DashboardPage() {
  const [pairs, setPairs] = useState<PairCardType[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPairs().then(setPairs).catch((err) => setError(err instanceof Error ? err.message : "Could not load pairs"));
  }, []);

  return (
    <ProtectedPage>
      <div className="headline" style={{ marginBottom: 18 }}>
        <div>
          <div className="kicker">Desk Overview</div>
          <h2>Four core pairs, one operator surface</h2>
        </div>
      </div>
      {error ? <div className="panel" style={{ color: "var(--danger)" }}>{error}</div> : null}
      <div className="grid-2">
        {pairs.map((pair) => (
          <PairCard key={pair.pair_id} pair={pair} />
        ))}
      </div>
    </ProtectedPage>
  );
}
