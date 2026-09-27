from abc import ABC, abstractmethod
from sdk.agenttrust.models import AgentRequest, AgentResponse


class AgentTrustAdapter(ABC):
    """
    Standard SDK interface for integrating any custom AI agent with AgentTrust.
    Implement `run` to connect internal agents directly without exposing them over HTTP.
    """

    @abstractmethod
    async def run(self, request: AgentRequest) -> AgentResponse:
        """
        Process the evaluation request and return a structured AgentResponse.
        """
        pass
