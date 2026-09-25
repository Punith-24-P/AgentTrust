from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = ""
    adapter_type: str = "demo"  # "demo" or "http"
    endpoint: Optional[str] = None
    version: str = "1.0.0"
    model: str = "default"
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "kn", "hi", "te"])
    config_json: Dict[str, Any] = Field(default_factory=dict)


class AgentCreate(AgentBase):
    project_id: str


class AgentResponse(AgentBase):
    id: str
    project_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
