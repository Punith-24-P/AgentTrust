import sys
import os
import time
from datetime import datetime, timezone

# Add workspace root to sys.path to import sdk
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sdk.agenttrust import (
    AgentTrustAdapter,
    AgentRequest,
    AgentResponse,
    Citation,
    RetrievedDocument,
    TraceStep,
)


class CustomEnterpriseAgent(AgentTrustAdapter):
    """
    Example enterprise support agent implementing AgentTrustAdapter.
    Demonstrates retrieval, MCP tool call trace emission, and multilingual answer generation.
    """

    async def run(self, request: AgentRequest) -> AgentResponse:
        trace = []
        retrieved_docs = []
        citations = []

        # Step 1: Observable retrieval tool step
        trace.append(
            TraceStep(
                step=1,
                type="retrieval",
                protocol="mcp",
                server="document_store",
                tool="search_sections",
                arguments={"query": request.question, "language": request.language},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        )

        # Simulated or actual document lookup
        sample_doc = RetrievedDocument(
            document_id="ENTERPRISE-SLA-2026",
            chunk_id="sla-sec-4",
            text="Priority-1 issues require a mandatory root cause investigation within 14 business days.",
            score=0.94
        )
        retrieved_docs.append(sample_doc)

        # Step 2: Observable calculation / tool call step
        trace.append(
            TraceStep(
                step=2,
                type="tool_call",
                tool="calculate_sla_window",
                input={"issue_type": "P1", "statutory_days": 14},
                output={"sla_deadline_days": 14},
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        )

        # Step 3: Observable generation step
        trace.append(
            TraceStep(
                step=3,
                type="generation",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        )

        citations.append(
            Citation(
                document_id="ENTERPRISE-SLA-2026",
                section="Section 4",
                text="Priority-1 issues require a mandatory root cause investigation within 14 business days."
            )
        )

        # Build answer tailored to question language
        if request.language == "kn":
            answer = "ಆದ್ಯತೆ-1 ಸಮಸ್ಯೆಗಳಿಗೆ 14 ಕೆಲಸದ ದಿನಗಳೊಳಗೆ ಕಡ್ಡಾಯ ತನಿಖೆ ನಡೆಸಬೇಕು."
        elif request.language == "hi":
            answer = "प्राथमिकता-1 मुद्दों की अनिवार्य जांच 14 कार्य दिवसों के भीतर की जानी चाहिए।"
        elif request.language == "te":
            answer = "ప్రాధాన్యత-1 సమస్యలపై 14 పని దినాలలో తప్పనిసరి విచారణ పూర్తి చేయాలి."
        else:
            answer = "According to Section 4 of the SLA, Priority-1 issues require a mandatory root cause investigation within 14 business days."

        return AgentResponse(
            answer=answer,
            language=request.language,
            citations=citations,
            retrieved_documents=retrieved_docs,
            trace=trace,
            metadata={"model": "enterprise-agent-v2", "version": "2.1.0"}
        )


# Expose as standalone HTTP server using FastAPI if executed directly
if __name__ == "__main__":
    import asyncio
    import uvicorn
    from fastapi import FastAPI

    agent = CustomEnterpriseAgent()
    app = FastAPI(title="Sample AgentTrust-Compatible Agent")

    @app.post("/run")
    async def run_agent_endpoint(req: AgentRequest):
        res = await agent.run(req)
        return res.model_dump()

    @app.get("/health")
    async def health():
        return {"status": "ok", "agent": "CustomEnterpriseAgent", "version": "2.1.0"}

    print("Starting sample agent microservice on http://127.0.0.1:5002 ...")
    uvicorn.run(app, host="0.0.0.0", port=5002)
