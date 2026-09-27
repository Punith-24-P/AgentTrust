export interface User {
  id: string;
  name: string;
  email: string;
  is_active: boolean;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  created_at: string;
}

export interface Project {
  id: string;
  workspace_id?: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  adapter_type: "demo" | "http";
  endpoint?: string;
  version: string;
  model: string;
  supported_languages: string[];
  config_json?: Record<string, any>;
  created_at: string;
}

export interface AgentConnectionTestResult {
  status: "SUCCESS" | "ERROR";
  latency_ms: number;
  status_code?: number;
  message: string;
  details: Record<string, any>;
}

export interface RequiredFact {
  id: string;
  type: string;
  expected: string;
  description?: string;
}

export interface SourceDocumentRef {
  document_id: string;
  section_id?: string;
}

export interface TestCase {
  id: string;
  dataset_id: string;
  version?: string;
  external_id: string;
  language: string;
  category: string;
  question: string;
  expected_answer: string;
  source_documents: SourceDocumentRef[];
  required_facts: RequiredFact[];
  potential_traps: string[];
  expected_retrieval?: boolean;
  expected_tools?: string[];
  created_at: string;
}

export interface DatasetVersion {
  id: string;
  dataset_id: string;
  version: string;
  is_published: boolean;
  test_cases_count: number;
  changelog?: string;
  created_at: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  version: string;
  test_cases_count?: number;
  versions?: DatasetVersion[];
  created_at: string;
}

export interface DatasetValidationIssue {
  test_case_id?: string;
  level: "ERROR" | "WARNING";
  field: string;
  message: string;
}

export interface DatasetValidationReport {
  dataset_id: string;
  is_valid: boolean;
  total_test_cases: number;
  errors_count: number;
  warnings_count: number;
  issues: DatasetValidationIssue[];
  languages: string[];
}

export interface EvaluationProfile {
  id: string;
  workspace_id?: string;
  name: string;
  description?: string;
  checks: Record<string, boolean>;
  weights: Record<string, number>;
  thresholds: Record<string, any>;
  is_default: boolean;
  created_at: string;
}

export interface TraceEvent {
  step: number;
  event_type: string;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  metadata_json?: Record<string, any>;
  timestamp: string;
}

export interface ClaimResult {
  claim_text: string;
  status: "SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED";
  document_id?: string;
  section_id?: string;
  evidence_text: string;
  reason: string;
}

export interface CitationResult {
  citation_text: string;
  status: "VALID" | "INVALID_SOURCE" | "INVALID_SECTION" | "MISMATCH" | "UNSUPPORTED" | "MISSING";
  document_id?: string;
  section_id?: string;
  evidence_matches: boolean;
  reason: string;
}

export interface TestResultItem {
  id: string;
  run_id: string;
  test_case_id: string;
  external_id: string;
  category: string;
  language: string;
  question: string;
  expected_answer: string;
  final_answer: string;
  latency_ms: number;
  status: string;
  retrieved_documents: any[];
  citations: string[];
  evaluation_result: {
    id: string;
    overall_status: "PASS" | "FAIL";
    composite_score: number;
    severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    correctness_status: string;
    correctness_score: number;
    correctness_reason: string;
    deterministic_score: number;
    semantic_score: number;
    grounding_status: string;
    grounding_score: number;
    grounding_reason: string;
    citation_status: string;
    citation_score: number;
    citation_reason: string;
    translation_status: string;
    translation_score: number;
    translation_reason: string;
    back_translation?: string;
    trajectory_status: string;
    trajectory_score: number;
    trajectory_reason: string;
    claims: ClaimResult[];
    citations: CitationResult[];
  };
  trace_events: TraceEvent[];
}

export interface RunItem {
  id: string;
  project_id: string;
  agent_id: string;
  dataset_id: string;
  agent_version: string;
  dataset_version: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "PARTIAL" | "CANCELLED";
  is_demo?: boolean;
  evaluation_profile_id?: string;
  evaluators_config: Record<string, boolean>;
  total_tests: number;
  completed_tests: number;
  composite_score?: number;
  duration_seconds?: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  created_at: string;
  agent_name?: string;
  dataset_name?: string;
}

export interface LanguageMetric {
  total_tests: number;
  passed_tests: number;
  pass_rate: number;
  composite_score: number;
  correctness_score: number;
  grounding_score: number;
  citation_score: number;
  translation_score: number;
  trajectory_score: number;
}

export interface RunMetrics {
  composite_score: number;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  overall_pass_rate: number;
  correctness: {
    score: number;
    pass_rate: number;
    total: number;
    passed: number;
    failed: number;
  };
  grounding: {
    score: number;
    supported_rate: number;
    claims_total: number;
    supported: number;
    unsupported: number;
    contradicted: number;
  };
  citation: {
    score: number;
    valid_rate: number;
    citations_total: number;
    valid: number;
    invalid: number;
    mismatch: number;
    missing: number;
  };
  translation: {
    score: number;
    pass_rate: number;
    minor_drift_rate: number;
    major_drift_rate: number;
    evaluated_tests: number;
  };
  trajectory: {
    score: number;
    retrieval_rate: number;
    loop_rate: number;
    pass_rate: number;
  };
  severity_breakdown: Record<string, number>;
  language_breakdown: Record<string, LanguageMetric>;
}

export interface ComparisonDelta {
  before: number;
  after: number;
  delta: number;
  improved: boolean;
}

export interface RunComparison {
  before_run_id: string;
  after_run_id: string;
  before_agent_name: string;
  after_agent_name: string;
  before_version: string;
  after_version: string;
  metrics: Record<string, ComparisonDelta>;
  language_deltas: Record<string, Record<string, ComparisonDelta>>;
}

export interface PreFlightResult {
  status: "READY" | "BLOCKED";
  agent_reachable: boolean;
  dataset_valid: boolean;
  evaluation_profile_valid: boolean;
  llm_provider_configured: boolean;
  documents_available: boolean;
  total_test_cases: number;
  issues: string[];
  warnings: string[];
}

export interface RegressionTestCase {
  test_case_id: string;
  external_id: string;
  language: string;
  question: string;
  baseline_status: string;
  current_status: string;
  change_type: "REGRESSION" | "IMPROVEMENT" | "UNCHANGED";
  baseline_score: number;
  current_score: number;
  failure_reason?: string;
  severity?: string;
}

export interface RegressionAnalysis {
  baseline_run_id: string;
  current_run_id: string;
  regression_detected: boolean;
  regressions_count: number;
  improvements_count: number;
  unchanged_count: number;
  test_cases: RegressionTestCase[];
}
