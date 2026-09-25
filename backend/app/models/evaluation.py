from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    test_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)

    # Correctness
    correctness_status: Mapped[str] = mapped_column(String(50), default="PASS")  # PASS, PARTIAL, FAIL, SKIPPED, ERROR
    correctness_score: Mapped[float] = mapped_column(Float, default=1.0)
    correctness_reason: Mapped[str] = mapped_column(Text, default="")
    deterministic_score: Mapped[float] = mapped_column(Float, default=1.0)
    semantic_score: Mapped[float] = mapped_column(Float, default=1.0)

    # Grounding
    grounding_status: Mapped[str] = mapped_column(String(50), default="SUPPORTED")  # SUPPORTED, UNSUPPORTED, CONTRADICTED
    grounding_score: Mapped[float] = mapped_column(Float, default=1.0)
    grounding_reason: Mapped[str] = mapped_column(Text, default="")
    claims_count: Mapped[int] = mapped_column(default=0)
    supported_claims_count: Mapped[int] = mapped_column(default=0)
    unsupported_claims_count: Mapped[int] = mapped_column(default=0)
    contradicted_claims_count: Mapped[int] = mapped_column(default=0)

    # Citation
    citation_status: Mapped[str] = mapped_column(
        String(50), default="VALID"
    )  # VALID, INVALID_SOURCE, INVALID_SECTION, MISMATCH, UNSUPPORTED, MISSING, NA
    citation_score: Mapped[float] = mapped_column(Float, default=1.0)
    citation_reason: Mapped[str] = mapped_column(Text, default="")

    # Translation
    translation_status: Mapped[str] = mapped_column(
        String(50), default="PASS"
    )  # PASS, MINOR_DRIFT, MAJOR_DRIFT, FAIL, NA
    translation_score: Mapped[float] = mapped_column(Float, default=1.0)
    translation_reason: Mapped[str] = mapped_column(Text, default="")
    back_translation: Mapped[str] = mapped_column(Text, default="")

    # Trajectory
    trajectory_status: Mapped[str] = mapped_column(String(50), default="PASS")  # PASS, WARNING, FAIL
    trajectory_score: Mapped[float] = mapped_column(Float, default=1.0)
    trajectory_reason: Mapped[str] = mapped_column(Text, default="")
    retrieval_executed: Mapped[bool] = mapped_column(Boolean, default=True)
    loop_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    sequence_valid: Mapped[bool] = mapped_column(Boolean, default=True)

    # Overall & Severity
    overall_status: Mapped[str] = mapped_column(String(50), default="PASS")  # PASS, FAIL
    composite_score: Mapped[float] = mapped_column(Float, default=1.0)
    severity: Mapped[str] = mapped_column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL

    # Detailed Evaluator Output Payload
    raw_evaluation: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    agent_run = relationship("AgentRun", back_populates="evaluation_result")
    claims = relationship("ClaimResult", back_populates="evaluation_result", cascade="all, delete-orphan")
    citations = relationship("CitationResult", back_populates="evaluation_result", cascade="all, delete-orphan")


class ClaimResult(Base):
    __tablename__ = "claim_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_result_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_results.id", ondelete="CASCADE"), nullable=False
    )
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # SUPPORTED, UNSUPPORTED, CONTRADICTED
    document_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    section_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_text: Mapped[str] = mapped_column(Text, default="")
    reason: Mapped[str] = mapped_column(Text, default="")

    # Relationships
    evaluation_result = relationship("EvaluationResult", back_populates="claims")


class CitationResult(Base):
    __tablename__ = "citation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_result_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("evaluation_results.id", ondelete="CASCADE"), nullable=False
    )
    citation_text: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # VALID, INVALID_SOURCE, INVALID_SECTION, MISMATCH, UNSUPPORTED, MISSING
    document_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    section_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_matches: Mapped[bool] = mapped_column(Boolean, default=True)
    reason: Mapped[str] = mapped_column(Text, default="")

    # Relationships
    evaluation_result = relationship("EvaluationResult", back_populates="citations")
