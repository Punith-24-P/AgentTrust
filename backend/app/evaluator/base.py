from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EvaluationContext(BaseModel):
    test_case: Dict[str, Any]
    agent_result: Dict[str, Any]
    evaluators_config: Dict[str, bool] = Field(default_factory=dict)


class EvaluatorOutput(BaseModel):
    name: str
    status: str  # PASS, PARTIAL, FAIL, WARNING, SKIPPED, ERROR
    score: float  # 0.0 to 1.0
    reason: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)


class BaseEvaluator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        """
        Executes evaluation logic on the provided context.
        Must handle errors gracefully and never raise unhandled exceptions.
        """
        pass
