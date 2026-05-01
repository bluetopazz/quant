"use client";

import { useState } from "react";

import { runPair } from "@/lib/api";
import { PairRunResult } from "@/lib/types";

export function useRunPair(pairId: string, onComplete?: (result: PairRunResult) => void) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    setRunning(true);
    setError(null);
    try {
      const result = await runPair(pairId);
      onComplete?.(result);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Pair run failed";
      setError(message);
      throw err;
    } finally {
      setRunning(false);
    }
  };

  return { execute, running, error };
}
