"use client";

import { useEffect, useState } from "react";

import { ProtectedPage } from "@/components/auth/ProtectedPage";
import { JournalTable } from "@/components/journal/JournalTable";
import { fetchAllJournals } from "@/lib/api";
import { JournalEntry } from "@/lib/types";

export default function JournalsPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAllJournals().then(setEntries).catch((err) => setError(err instanceof Error ? err.message : "Could not load journals"));
  }, []);

  return (
    <ProtectedPage>
      <div className="headline" style={{ marginBottom: 18 }}>
        <div>
          <div className="kicker">Archive</div>
          <h2>Journal and reasoning history</h2>
        </div>
      </div>
      {error ? <div className="panel" style={{ color: "var(--danger)" }}>{error}</div> : null}
      <JournalTable entries={entries} />
    </ProtectedPage>
  );
}
