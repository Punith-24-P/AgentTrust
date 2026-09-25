from datetime import datetime, timezone
import uuid
from typing import Any
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TraceEvent(Base):
    __tablename__ = "trace_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # agent_start, retrieval, tool_call, tool_result, generation, translation, agent_end, error
    input_data: Mapped[Any] = mapped_column(JSON, default=dict)
    output_data: Mapped[Any] = mapped_column(JSON, default=dict)
    metadata_json: Mapped[Any] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    agent_run = relationship("AgentRun", back_populates="trace_events")
