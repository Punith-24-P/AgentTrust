import time
from typing import Dict, Any, Optional
import httpx
from app.agents.base import BaseAgentAdapter, AgentRunResult


class HTTPAgentAdapter(BaseAgentAdapter):
    """
    Adapter for evaluating external user-hosted AI agents via HTTP API.
    Sends standard test case payload and parses observable execution output.
    """

    def __init__(self, endpoint: str, timeout_sec: float = 30.0):
        self.endpoint = endpoint
        self.timeout_sec = timeout_sec

    async def run(self, test_case: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> AgentRunResult:
        start_time = time.time()
        payload = {
            "test_case_id": test_case.get("id"),
            "question": test_case.get("question"),
            "language": test_case.get("language", "en"),
            "category": test_case.get("category", "general"),
            "source_documents": test_case.get("source_documents", []),
            "metadata": config or {}
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_sec) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                latency_ms = int((time.time() - start_time) * 1000)
                return AgentRunResult(
                    final_answer=data.get("final_answer", data.get("answer", "")),
                    language=data.get("language", test_case.get("language", "en")),
                    retrieved_documents=data.get("retrieved_documents", data.get("documents", [])),
                    citations=data.get("citations", []),
                    trace=data.get("trace", []),
                    metadata=data.get("metadata", {}),
                    latency_ms=data.get("latency_ms", latency_ms),
                    status="SUCCESS"
                )
        except httpx.HTTPStatusError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return AgentRunResult(
                final_answer="",
                language=test_case.get("language", "en"),
                latency_ms=latency_ms,
                status="AGENT_ERROR",
                error_message=f"HTTP Agent returned error status {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return AgentRunResult(
                final_answer="",
                language=test_case.get("language", "en"),
                latency_ms=latency_ms,
                status="AGENT_ERROR",
                error_message=f"Failed to communicate with external agent at {self.endpoint}: {str(e)}"
            )
