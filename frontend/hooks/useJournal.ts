"use client";

import { useEffect, useState } from "react";

import { appendJournal, fetchPairJournals } from "@/lib/api";
import { JournalEntry } from "@/lib/types";

export function useJournal(pairId: string) {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      setEntries(await fetchPairJournals(pairId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load journal history");
    } finally {
      setLoading(false);
    }
  };

  const append = async (runId: string) => {
    const entry = await appendJournal(pairId, runId);
    await refresh();
    return entry;
  };

  useEffect(() => {
    void refresh();
  }, [pairId]);

  return { entries, loading, error, refresh, append };
}
