from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.evaluation_profile import EvaluationProfile
from app.models.user import User
from app.schemas.evaluation_profile import EvaluationProfileCreate, EvaluationProfileResponse
from app.api.deps import get_optional_user, log_audit_event

router = APIRouter(prefix="/evaluation-profiles", tags=["Evaluation Profiles"])

DEFAULT_PROFILES = [
    {
        "name": "Balanced Multilingual Reliability",
        "description": "Standard evaluation: 30% correctness, 30% grounding, 15% citation, 15% translation, 10% trajectory.",
        "checks": {"correctness": True, "grounding": True, "citation": True, "translation": True, "trajectory": True},
        "weights": {"correctness": 0.30, "grounding": 0.30, "citation": 0.15, "translation": 0.15, "trajectory": 0.10},
        "thresholds": {"semantic_pass_threshold": 0.70, "translation_fidelity_threshold": 0.75, "max_repeated_tool_calls": 3, "min_evidence_required": 1},
        "is_default": True
    },
    {
        "name": "Strict Evidence & Fact Grounding",
        "description": "High-assurance grounding profile: 40% grounding, 30% correctness, 20% citation, 10% trajectory.",
        "checks": {"correctness": True, "grounding": True, "citation": True, "translation": False, "trajectory": True},
        "weights": {"correctness": 0.30, "grounding": 0.40, "citation": 0.20, "translation": 0.00, "trajectory": 0.10},
        "thresholds": {"semantic_pass_threshold": 0.85, "translation_fidelity_threshold": 0.80, "max_repeated_tool_calls": 2, "min_evidence_required": 1},
        "is_default": False
    },
    {
        "name": "Multilingual Translation Audit",
        "description": "Cross-lingual evaluation focusing on preserving critical obligations and terms across languages.",
        "checks": {"correctness": True, "grounding": True, "citation": False, "translation": True, "trajectory": False},
        "weights": {"correctness": 0.35, "grounding": 0.25, "citation": 0.00, "translation": 0.40, "trajectory": 0.00},
        "thresholds": {"semantic_pass_threshold": 0.75, "translation_fidelity_threshold": 0.80, "max_repeated_tool_calls": 3, "min_evidence_required": 1},
        "is_default": False
    }
]


@router.get("", response_model=List[EvaluationProfileResponse])
async def list_evaluation_profiles(
    workspace_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(EvaluationProfile)
    if workspace_id:
        query = query.where((EvaluationProfile.workspace_id == workspace_id) | (EvaluationProfile.workspace_id.is_(None)))
    result = await db.execute(query)
    profiles = result.scalars().all()

    # If database is empty, seed defaults
    if not profiles:
        for p_data in DEFAULT_PROFILES:
            prof = EvaluationProfile(**p_data)
            db.add(prof)
        await db.flush()
        result = await db.execute(select(EvaluationProfile))
        profiles = result.scalars().all()

    return [EvaluationProfileResponse.model_validate(p) for p in profiles]


@router.post("", response_model=EvaluationProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation_profile(
    req: EvaluationProfileCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    profile = EvaluationProfile(
        name=req.name,
        description=req.description,
        workspace_id=req.workspace_id,
        checks=req.checks,
        weights=req.weights,
        thresholds=req.thresholds,
        is_default=req.is_default,
    )
    db.add(profile)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="EVALUATION_PROFILE_CREATED",
            entity_type="evaluation_profile",
            entity_id=profile.id,
            user_id=current_user.id,
            workspace_id=req.workspace_id,
            details={"name": profile.name}
        )

    return EvaluationProfileResponse.model_validate(profile)
