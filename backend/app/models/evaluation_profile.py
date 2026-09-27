from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class EvaluationProfile(Base):
    __tablename__ = "evaluation_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")
    checks: Mapped[Any] = mapped_column(
        JSON,
        default=lambda: {
            "correctness": True,
            "grounding": True,
            "citation": True,
            "translation": True,
            "trajectory": True,
        }
    )
    weights: Mapped[Any] = mapped_column(
        JSON,
        default=lambda: {
            "correctness": 0.30,
            "grounding": 0.30,
            "citation": 0.15,
            "translation": 0.15,
            "trajectory": 0.10,
        }
    )
    thresholds: Mapped[Any] = mapped_column(
        JSON,
        default=lambda: {
            "semantic_pass_threshold": 0.70,
            "translation_fidelity_threshold": 0.75,
            "max_repeated_tool_calls": 3,
            "min_evidence_required": 1,
        }
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
