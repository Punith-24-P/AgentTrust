from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class EvaluationProfileBase(BaseModel):
    name: str
    description: Optional[str] = ""
    checks: Dict[str, bool] = Field(
        default_factory=lambda: {
            "correctness": True,
            "grounding": True,
            "citation": True,
            "translation": True,
            "trajectory": True,
        }
    )
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "correctness": 0.30,
            "grounding": 0.30,
            "citation": 0.15,
            "translation": 0.15,
            "trajectory": 0.10,
        }
    )
    thresholds: Dict[str, Any] = Field(
        default_factory=lambda: {
            "semantic_pass_threshold": 0.70,
            "translation_fidelity_threshold": 0.75,
            "max_repeated_tool_calls": 3,
            "min_evidence_required": 1,
        }
    )
    is_default: bool = False


class EvaluationProfileCreate(EvaluationProfileBase):
    workspace_id: Optional[str] = None


class EvaluationProfileResponse(EvaluationProfileBase):
    id: str
    workspace_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
