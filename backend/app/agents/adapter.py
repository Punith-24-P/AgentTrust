from typing import Optional, Dict, Any
from app.agents.base import BaseAgentAdapter, AgentRunResult
from app.agents.demo_agent import DemoAgentAdapter
from app.agents.http_agent import HTTPAgentAdapter


def get_agent_adapter(
    adapter_type: str,
    endpoint: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> BaseAgentAdapter:
    """
    Factory creating appropriate AgentAdapter based on registration metadata.
    """
    config = config or {}
    if adapter_type.lower() == "http":
        if not endpoint:
            raise ValueError("Endpoint URL required for HTTP agent adapter.")
        return HTTPAgentAdapter(endpoint=endpoint, timeout_sec=config.get("timeout_sec", 30.0))

    # Default to DemoAgentAdapter
    simulation_rates = config.get("simulation_rates")
    return DemoAgentAdapter(failure_modes=simulation_rates)


__all__ = [
    "BaseAgentAdapter",
    "AgentRunResult",
    "DemoAgentAdapter",
    "HTTPAgentAdapter",
    "get_agent_adapter",
]
