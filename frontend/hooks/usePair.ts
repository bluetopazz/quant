"use client";

import { useEffect, useState } from "react";

import { fetchLatestRun, fetchPair, fetchPairHistory } from "@/lib/api";
import { PairDetail, PairRunResult, PairRunSummary } from "@/lib/types";

export function usePair(pairId: string) {
  const [detail, setDetail] = useState<PairDetail | null>(null);
  const [latest, setLatest] = useState<PairRunResult | null>(null);
  const [history, setHistory] = useState<PairRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const detailData = await fetchPair(pairId);
      setDetail(detailData);
      try {
        setLatest(await fetchLatestRun(pairId));
      } catch {
        setLatest(null);
      }
      setHistory(await fetchPairHistory(pairId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load pair");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, [pairId]);

  return { detail, latest, history, loading, error, refresh, setLatest };
}
