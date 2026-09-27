from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    dataset_id: Mapped[str] = mapped_column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    agent_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    dataset_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED, PARTIAL, CANCELLED
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    evaluation_profile_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    evaluation_profile_json: Mapped[Any] = mapped_column(JSON, default=dict)
    evaluators_config: Mapped[Any] = mapped_column(
        JSON,
        default=lambda: {
            "correctness": True,
            "grounding": True,
            "citation": True,
            "translation": True,
            "trajectory": True
        }
    )
    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    completed_tests: Mapped[int] = mapped_column(Integer, default=0)
    composite_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="runs")
    agent = relationship("Agent", back_populates="runs")
    dataset = relationship("Dataset", back_populates="runs")
    agent_runs = relationship("AgentRun", back_populates="run", cascade="all, delete-orphan")
    metric = relationship("RunMetric", back_populates="run", uselist=False, cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    test_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    final_answer: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(10), default="en")
    retrieved_documents: Mapped[Any] = mapped_column(JSON, default=list)
    citations: Mapped[Any] = mapped_column(JSON, default=list)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS")  # SUCCESS, AGENT_ERROR
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    run = relationship("Run", back_populates="agent_runs")
    test_case = relationship("TestCase")
    trace_events = relationship("TraceEvent", back_populates="agent_run", cascade="all, delete-orphan")
    evaluation_result = relationship("EvaluationResult", back_populates="agent_run", uselist=False, cascade="all, delete-orphan")


class RunMetric(Base):
    __tablename__ = "run_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    metrics_json: Mapped[Any] = mapped_column(JSON, default=dict)
    language_metrics_json: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    run = relationship("Run", back_populates="metric")
