export type PairRunSummary = {
  run_id: string;
  pair_id: string;
  status: string;
  run_timestamp: string;
  warning_count: number;
  error_code?: string | null;
  error_message?: string | null;
};

export type PairCard = {
  pair_id: string;
  notebook_name: string;
  theme: string;
  relationship: string;
  prompt_style: string;
  parser_style: string;
  signal_shape: string;
  latest_run?: PairRunSummary | null;
};

export type PairDetail = {
  pair_id: string;
  notebook_name: string;
  theme: string;
  relationship: string;
  yfinance_tickers: string[];
  fred_series_ids: string[];
  prompt_style: string;
  parser_style: string;
  signal_shape: string;
  external_apis: string[];
  feature_flags: string[];
  special_handling_rules: string[];
  chart_metadata: Record<string, string>;
  latest_run?: PairRunSummary | null;
};

export type RunWarning = {
  warning_code: string;
  stage: string;
  message: string;
  source?: string | null;
  field?: string | null;
  severity?: string | null;
  recoverable: boolean;
};

export type RunError = {
  error_code: string;
  stage: string;
  message: string;
  source?: string | null;
  retryable: boolean;
  details?: Record<string, unknown> | null;
};

export type FeatureSnapshot = {
  pair_id: string;
  as_of_date: string;
  core_metrics: Record<string, unknown>;
  pair_extensions: Record<string, unknown>;
  normalization_mode: string;
  source_freshness?: Record<string, unknown> | null;
};

export type ChartPayload = {
  chart_id: string;
  pair_id: string;
  family: string;
  title: string;
  render_kind: string;
  x_axis: {
    label: string;
    values: string[];
  };
  series: Array<{
    series_id: string;
    label: string;
    axis?: string | null;
    values: Array<number | null>;
  }>;
};

export type AnalystMemo = {
  memo_id: string;
  pair_id: string;
  content: string;
  model_name: string;
  prompt_version: string;
  prompt_style?: string | null;
  prompt_template_id?: string | null;
  system_role?: string | null;
  temperature?: number | null;
  timeout_seconds?: number | null;
  generated_at?: string | null;
  source_summary?: Record<string, unknown> | null;
};

export type ParsedSignal = {
  pair_id: string;
  signal_style: string;
  parser_style: string;
  parser_version: string;
  parse_status: string;
  directional_bias?: string | null;
  confidence?: string | null;
  notes?: string | null;
  target_asset?: string | null;
  strategy?: string | null;
  left_leg_label?: string | null;
  right_leg_label?: string | null;
  left_strategy?: string | null;
  right_strategy?: string | null;
  parser_input_memo_id?: string | null;
  used_llm_second_pass: boolean;
  fallback_reason?: string | null;
  raw_parser_output?: string | null;
};

export type RiskTicket = {
  pair_id: string;
  sizing_mode: string;
  account_value_assumption: number;
  risk_bps_per_trade: number;
  total_risk_budget_usd?: number | null;
  sizing_status: string;
  notes?: string | null;
  target_asset?: string | null;
  strategy?: string | null;
  contracts?: number | null;
  risk_budget_usd?: number | null;
  left_strategy?: string | null;
  right_strategy?: string | null;
  left_contracts?: number | null;
  right_contracts?: number | null;
  per_leg_budget_usd?: number | null;
  total_budget_usd?: number | null;
  strategy_risk_table_version?: string | null;
  heuristic_name?: string | null;
  sizing_assumptions?: Record<string, unknown> | null;
};

export type JournalEntryPreview = {
  pair_id: string;
  journal_schema_version: string;
  journal_mode: string;
  preview_payload: Record<string, unknown>;
};

export type PairRunResult = {
  run_id: string;
  pair_id: string;
  status: string;
  run_timestamp: string;
  feature_snapshot: FeatureSnapshot;
  charts: ChartPayload[];
  analyst_memo?: AnalystMemo | null;
  parsed_signal?: ParsedSignal | null;
  risk_ticket?: RiskTicket | null;
  journal_entry_preview?: JournalEntryPreview | null;
  warnings: RunWarning[];
  error?: RunError | null;
  notebook_reference?: string | null;
  theme?: string | null;
  relationship?: string | null;
  pair_prompt_style?: string | null;
  pair_signal_style?: string | null;
  requested_by_user_id?: string | null;
  trigger_source?: string | null;
  prompt_version?: string | null;
  engine_version?: string | null;
  persistence_summary?: Record<string, unknown> | null;
};

export type JournalEntry = {
  id?: number | null;
  pair_id: string;
  run_id?: string | null;
  appended_at?: string | null;
  csv_path?: string | null;
  payload: Record<string, unknown>;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    role: string;
  };
};

export type AttentionFlag = {
  pair_id: string;
  pair_ids: string[];
  severity: string;
  title: string;
  reason: string;
  metric_key?: string | null;
  metric_value?: number | null;
};

export type ChangeSummary = {
  pair_id: string;
  title: string;
  description: string;
  changed_at?: string | null;
  absolute_zscore_change?: number | null;
  velocity_change?: number | null;
  corr_90d_change?: number | null;
  driver_change_key?: string | null;
  driver_change_value?: number | null;
  attention_score?: number | null;
};

export type PairStateSnapshot = {
  snapshot_id: string;
  pair_id: string;
  source_run_id: string;
  snapshot_timestamp: string;
  run_timestamp?: string | null;
  as_of_date: string;
  status: string;
  staleness_status: string;
  theme?: string | null;
  relationship?: string | null;
  signal_zscore?: number | null;
  signal_velocity_5d?: number | null;
  corr_30d?: number | null;
  corr_90d?: number | null;
  ratio?: number | null;
  spread_value?: number | null;
  directional_bias?: string | null;
  confidence?: string | null;
  regime_label?: string | null;
  vol_regime?: string | null;
  driver_label?: string | null;
  driver_value?: number | null;
  secondary_driver_label?: string | null;
  secondary_driver_value?: number | null;
  attention_score: number;
  warning_count: number;
  pair_extensions: Record<string, unknown>;
  source_freshness?: Record<string, unknown> | null;
};

export type PairTrajectoryPoint = {
  pair_id: string;
  run_id: string;
  run_timestamp: string;
  x_value?: number | null;
  y_value?: number | null;
  color_value?: number | null;
  regime_label?: string | null;
  region_label?: string | null;
  motion_label?: string | null;
  directional_bias?: string | null;
  confidence?: string | null;
  status: string;
  x_label: string;
  y_label: string;
  current: boolean;
};

export type CouplingSnapshot = {
  snapshot_timestamp: string;
  pair_ids: string[];
  matrix_metric: string;
  matrix: Array<Array<number | null>>;
  coherence_score?: number | null;
  fragmentation_score?: number | null;
  coherence_delta?: number | null;
  fragmentation_delta?: number | null;
};

export type DeskHistoryPoint = {
  snapshot_timestamp: string;
  coherence_score?: number | null;
  fragmentation_score?: number | null;
  stress_score?: number | null;
  dominant_regime?: string | null;
};

export type RefreshStatus = {
  refresh_id?: string | null;
  status: string;
  trigger_source?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  total_pairs: number;
  success_count: number;
  degraded_count: number;
  failed_count: number;
  warning_count: number;
  warnings: string[];
  error_message?: string | null;
};

export type DeskStateSnapshot = {
  snapshot_id: string;
  snapshot_timestamp: string;
  latest_common_run_timestamp?: string | null;
  dominant_regime?: string | null;
  coherence_score?: number | null;
  fragmentation_score?: number | null;
  stress_score?: number | null;
  state_dispersion?: number | null;
  attention_pair_id?: string | null;
  coverage_ratio: number;
  stale_pair_ids: string[];
  freshness_status: string;
  degraded: boolean;
  pair_states: PairStateSnapshot[];
  coupling?: CouplingSnapshot | null;
  change_summaries: ChangeSummary[];
  attention_flags: AttentionFlag[];
  refresh_status?: RefreshStatus | null;
  desk_history: DeskHistoryPoint[];
};

export type IntelligenceOverview = {
  desk: DeskStateSnapshot;
  trajectories: Record<string, PairTrajectoryPoint[]>;
};
