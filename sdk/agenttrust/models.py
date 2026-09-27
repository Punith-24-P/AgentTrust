from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class Citation(BaseModel):
    document_id: str
    section: Optional[str] = None
    text: Optional[str] = None


class RetrievedDocument(BaseModel):
    document_id: str
    chunk_id: Optional[str] = None
    text: str
    score: Optional[float] = None


class TraceStep(BaseModel):
    step: int
    type: str  # "retrieval", "tool_call", "generation"
    protocol: Optional[str] = None  # e.g. "mcp"
    server: Optional[str] = None
    tool: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    input: Optional[Any] = None
    output: Optional[Any] = None
    timestamp: Optional[str] = None


class AgentRequest(BaseModel):
    question: str
    language: str = "en"
    test_case_id: Optional[str] = None
    category: Optional[str] = "general"
    source_documents: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    answer: str
    language: str = "en"
    citations: List[Citation] = Field(default_factory=list)
    retrieved_documents: List[RetrievedDocument] = Field(default_factory=list)
    trace: List[TraceStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
