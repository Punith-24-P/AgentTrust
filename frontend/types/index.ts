export interface Project {
  id: string;
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
  external_id: string;
  language: string;
  category: string;
  question: string;
  expected_answer: string;
  source_documents: SourceDocumentRef[];
  required_facts: RequiredFact[];
  potential_traps: string[];
  created_at: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  version: string;
  test_cases_count?: number;
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
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
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
