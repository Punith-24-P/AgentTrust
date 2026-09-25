from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentRunResult(BaseModel):
    final_answer: str
    language: str = "en"
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    status: str = "SUCCESS"  # SUCCESS | AGENT_ERROR
    error_message: Optional[str] = None


class BaseAgentAdapter(ABC):
    @abstractmethod
    async def run(self, test_case: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> AgentRunResult:
        """
        Execute an agent against a single structured test case.
        Captures observable trace, retrieved documents, citations, latency, and final answer.
        """
        pass
