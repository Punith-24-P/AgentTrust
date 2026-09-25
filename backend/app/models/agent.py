from datetime import datetime, timezone
import uuid
from typing import Optional, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    adapter_type: Mapped[str] = mapped_column(String(50), default="demo")  # "demo" or "http"
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    model: Mapped[str] = mapped_column(String(100), default="default")
    supported_languages: Mapped[Any] = mapped_column(JSON, default=lambda: ["en", "kn", "hi", "te"])
    config_json: Mapped[Any] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="agents")
    runs = relationship("Run", back_populates="agent", cascade="all, delete-orphan")
