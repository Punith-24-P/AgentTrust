from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.test_case import TestCaseResponse
from app.schemas.trace import TraceEventResponse
from app.schemas.evaluation import EvaluationResultResponse


class EvaluatorsConfigSchema(BaseModel):
    correctness: bool = True
    grounding: bool = True
    citation: bool = True
    translation: bool = True
    trajectory: bool = True


class RunCreate(BaseModel):
    project_id: str
    agent_id: str
    dataset_id: str
    agent_version: Optional[str] = None
    dataset_version: Optional[str] = None
    evaluation_profile_id: Optional[str] = None
    evaluators_config: Optional[EvaluatorsConfigSchema] = Field(default_factory=EvaluatorsConfigSchema)
    concurrency: Optional[int] = 4
    test_case_subset: Optional[List[str]] = None  # optional list of test case IDs
    is_demo: Optional[bool] = False


class RunResponse(BaseModel):
    id: str
    project_id: str
    agent_id: str
    dataset_id: str
    agent_version: str
    dataset_version: str
    status: str
    is_demo: bool = False
    evaluation_profile_id: Optional[str] = None
    evaluators_config: Dict[str, Any]
    total_tests: int
    completed_tests: int
    composite_score: Optional[float] = None
    duration_seconds: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    agent_name: Optional[str] = None
    dataset_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AgentRunDetailResponse(BaseModel):
    id: str
    run_id: str
    test_case_id: str
    final_answer: str
    language: str
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    latency_ms: int = 0
    status: str
    error_message: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    test_case: Optional[TestCaseResponse] = None
    trace_events: List[TraceEventResponse] = Field(default_factory=list)
    evaluation_result: Optional[EvaluationResultResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MetricCategorySummary(BaseModel):
    score: float
    pass_rate: float
    total: int
    passed: int
    failed: int


class RunMetricSummary(BaseModel):
    composite_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    overall_pass_rate: float

    correctness: Dict[str, Any]
    grounding: Dict[str, Any]
    citation: Dict[str, Any]
    translation: Dict[str, Any]
    trajectory: Dict[str, Any]
    severity_breakdown: Dict[str, int]
    language_breakdown: Dict[str, Dict[str, Any]]


class RunComparisonItem(BaseModel):
    before: float
    after: float
    delta: float  # after - before
    improved: bool


class RunComparisonResponse(BaseModel):
    before_run_id: str
    after_run_id: str
    before_agent_name: str
    after_agent_name: str
    before_version: str
    after_version: str
    metrics: Dict[str, RunComparisonItem]
    language_deltas: Dict[str, Dict[str, RunComparisonItem]]


class PreFlightCheckRequest(BaseModel):
    agent_id: str
    dataset_id: str
    dataset_version: Optional[str] = None
    evaluation_profile_id: Optional[str] = None


class PreFlightCheckResponse(BaseModel):
    status: str  # "READY" or "BLOCKED"
    agent_reachable: bool
    dataset_valid: bool
    evaluation_profile_valid: bool
    llm_provider_configured: bool
    documents_available: bool
    total_test_cases: int
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RegressionTestCase(BaseModel):
    test_case_id: str
    external_id: str
    language: str
    question: str
    baseline_status: str
    current_status: str
    change_type: str  # "REGRESSION", "IMPROVEMENT", "UNCHANGED"
    baseline_score: float
    current_score: float
    failure_reason: Optional[str] = ""
    severity: Optional[str] = "LOW"


class RegressionAnalysisResponse(BaseModel):
    baseline_run_id: str
    current_run_id: str
    regression_detected: bool
    regressions_count: int
    improvements_count: int
    unchanged_count: int
    test_cases: List[RegressionTestCase] = Field(default_factory=list)
