from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class TraceEventBase(BaseModel):
    step: int
    event_type: str  # agent_start, retrieval, tool_call, tool_result, generation, translation, agent_end, error
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class TraceEventCreate(TraceEventBase):
    agent_run_id: str


class TraceEventResponse(TraceEventBase):
    id: str
    agent_run_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
