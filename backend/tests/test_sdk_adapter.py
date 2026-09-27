import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from examples.sample_agent.custom_agent import CustomEnterpriseAgent
from sdk.agenttrust import AgentRequest


@pytest.mark.asyncio
async def test_custom_agent_adapter_execution():
    agent = CustomEnterpriseAgent()
    req = AgentRequest(
        question="What is the root cause deadline for Priority 1 issues?",
        language="en",
        test_case_id="TEST-SLA-01"
    )
    res = await agent.run(req)
    assert "14" in res.answer
    assert len(res.citations) == 1
    assert res.citations[0].document_id == "ENTERPRISE-SLA-2026"
    assert len(res.trace) == 3
    assert res.trace[0].protocol == "mcp"
    assert res.trace[0].type == "retrieval"
