from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ClaimResultResponse(BaseModel):
    id: str
    claim_text: str
    status: str  # SUPPORTED, UNSUPPORTED, CONTRADICTED
    document_id: Optional[str] = None
    section_id: Optional[str] = None
    evidence_text: str = ""
    reason: str = ""

    model_config = ConfigDict(from_attributes=True)


class CitationResultResponse(BaseModel):
    id: str
    citation_text: str
    status: str  # VALID, INVALID_SOURCE, INVALID_SECTION, MISMATCH, UNSUPPORTED, MISSING
    document_id: Optional[str] = None
    section_id: Optional[str] = None
    evidence_matches: bool = True
    reason: str = ""

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultResponse(BaseModel):
    id: str
    agent_run_id: str
    run_id: str
    test_case_id: str

    # Evaluators
    correctness_status: str
    correctness_score: float
    correctness_reason: str
    deterministic_score: float
    semantic_score: float

    grounding_status: str
    grounding_score: float
    grounding_reason: str
    claims_count: int
    supported_claims_count: int
    unsupported_claims_count: int
    contradicted_claims_count: int

    citation_status: str
    citation_score: float
    citation_reason: str

    translation_status: str
    translation_score: float
    translation_reason: str
    back_translation: str

    trajectory_status: str
    trajectory_score: float
    trajectory_reason: str
    retrieval_executed: bool
    loop_detected: bool
    sequence_valid: bool

    overall_status: str
    composite_score: float
    severity: str

    claims: List[ClaimResultResponse] = Field(default_factory=list)
    citations: List[CitationResultResponse] = Field(default_factory=list)
    raw_evaluation: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
