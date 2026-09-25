"""
Example standalone External AI Agent.
Demonstrates how any external agent framework (LangChain, LlamaIndex, CrewAI, AutoGen, custom)
can be plugged into AgentTrust via the standard HTTPAgentAdapter.

To run:
    python example_external_agent.py
Listens on: http://localhost:5001/run
"""

from typing import Dict, Any, List
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="External Sample Agent for AgentTrust")


class AgentRunRequest(BaseModel):
    test_case_id: str
    question: str
    language: str = "en"
    category: str = "general"
    source_documents: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    final_answer: str
    language: str
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    trace: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: int = 45


@app.post("/run", response_model=AgentRunResponse)
async def run_agent(req: AgentRunRequest):
    # Simulated external agent execution
    lang = req.language.lower()
    q = req.question.lower()

    # Document retrieval simulation
    retrieved = []
    if req.source_documents:
        first = req.source_documents[0]
        retrieved.append({
            "document_id": first.get("document_id", "DOC-CP-001"),
            "section_id": first.get("section_id", "§4"),
            "content": "Applications for gathering permits exceeding 150 attendees must be submitted at least 30 calendar days prior under §4."
        })

    # Response generation
    if lang == "kn":
        answer = "ನಾಗರಿಕ ಅನುಮತಿಗಳ ನಿರ್ದೇಶನದ §4 ರ ಪ್ರಕಾರ 150 ಕ್ಕಿಂತ ಹೆಚ್ಚು ಭಾಗವಹಿಸುವ ಕಾರ್ಯಕ್ರಮಗಳಿಗಾಗಿ ಕನಿಷ್ಠ 30 ಕ್ಯಾಲೆಂಡರ್ ದಿನಗಳ ಮುಂಚಿತವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು."
    elif lang == "hi":
        answer = "नागरिक अनुमति निर्देश के §4 के अनुसार 30 कैलेंडर दिन पहले आवेदन जमा करना अनिवार्य है।"
    elif lang == "te":
        answer = "పౌర అనుమతుల ఆదేశం యొక్క §4 ప్రకారం కనీసం 30 క్యాలెండర్ రోజుల ముందు దరఖాస్తు చేసుకోవాలి."
    else:
        answer = "Under §4 of DOC-CP-001, applications for civic gatherings exceeding 150 attendees must be submitted at least 30 calendar days prior to the event date."

    citations = ["DOC-CP-001 §4"]

    trace = [
        {"step": 1, "event_type": "agent_start", "input_data": {"question": req.question}, "output_data": {}},
        {"step": 2, "event_type": "retrieval", "input_data": {"query": req.question}, "output_data": {"docs": retrieved}},
        {"step": 3, "event_type": "generation", "input_data": {}, "output_data": {"answer": answer}},
        {"step": 4, "event_type": "agent_end", "input_data": {}, "output_data": {"status": "SUCCESS"}}
    ]

    return AgentRunResponse(
        final_answer=answer,
        language=req.language,
        retrieved_documents=retrieved,
        citations=citations,
        trace=trace,
        latency_ms=85
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
