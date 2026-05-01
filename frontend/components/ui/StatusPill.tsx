type Props = {
  status?: string | null;
};

export function StatusPill({ status }: Props) {
  const normalized = (status ?? "idle").toLowerCase();
  const className =
    normalized === "success"
      ? "status-pill status-success"
      : normalized === "degraded_success"
        ? "status-pill status-success"
      : normalized === "error"
        ? "status-pill status-error"
        : "status-pill status-idle";

  return <span className={className}>{normalized}</span>;
}
