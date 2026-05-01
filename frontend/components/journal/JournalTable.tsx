import { JournalEntry } from "@/lib/types";

export function JournalTable({ entries }: { entries: JournalEntry[] }) {
  if (!entries.length) {
    return <div className="empty-state">No journal history available yet.</div>;
  }

  const columns = Array.from(
    entries.reduce((acc, entry) => {
      Object.keys(entry.payload ?? {}).forEach((key) => acc.add(key));
      return acc;
    }, new Set<string>())
  ).slice(0, 8);

  return (
    <div className="table-wrap panel">
      <div className="headline" style={{ marginBottom: 12 }}>
        <h3>Journal History</h3>
      </div>
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, index) => (
            <tr key={`${entry.pair_id}-${entry.id ?? index}`}>
              {columns.map((column) => (
                <td key={column}>{String(entry.payload?.[column] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
