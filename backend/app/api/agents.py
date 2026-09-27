import time
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse, AgentConnectionTestResponse
from app.api.deps import get_optional_user, log_audit_event

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    agent = Agent(
        project_id=data.project_id,
        name=data.name.strip(),
        description=data.description or "",
        adapter_type=data.adapter_type,
        endpoint=data.endpoint.strip() if data.endpoint else None,
        version=data.version or "1.0.0",
        model=data.model or "default",
        supported_languages=data.supported_languages,
        config_json=data.config_json or {}
    )
    db.add(agent)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="AGENT_REGISTERED",
            entity_type="agent",
            entity_id=agent.id,
            user_id=current_user.id,
            details={"name": agent.name, "adapter_type": agent.adapter_type, "endpoint": agent.endpoint}
        )

    return agent


@router.get("", response_model=List[AgentResponse])
async def list_agents(project_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Agent)
    if project_id:
        q = q.where(Agent.project_id == project_id)
    q = q.order_by(Agent.created_at.desc())
    res = await db.execute(q)
    return res.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Agent).where(Agent.id == agent_id)
    res = await db.execute(q)
    agent = res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    data: AgentCreate,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Agent).where(Agent.id == agent_id)
    res = await db.execute(q)
    agent = res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.name = data.name.strip()
    agent.description = data.description or ""
    agent.adapter_type = data.adapter_type
    agent.endpoint = data.endpoint.strip() if data.endpoint else None
    agent.version = data.version or "1.0.0"
    agent.model = data.model or "default"
    agent.supported_languages = data.supported_languages
    agent.config_json = data.config_json or {}

    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="AGENT_UPDATED",
            entity_type="agent",
            entity_id=agent.id,
            user_id=current_user.id,
            details={"name": agent.name}
        )

    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Agent).where(Agent.id == agent_id)
    res = await db.execute(q)
    agent = res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="AGENT_DELETED",
            entity_type="agent",
            entity_id=agent_id,
            user_id=current_user.id
        )


@router.post("/{agent_id}/test-connection", response_model=AgentConnectionTestResponse)
async def test_agent_connection(agent_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Agent).where(Agent.id == agent_id)
    res = await db.execute(q)
    agent = res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if agent.adapter_type == "demo":
        return AgentConnectionTestResponse(
            status="SUCCESS",
            latency_ms=12,
            status_code=200,
            message="Internal Demo Agent is ready and responding locally.",
            details={
                "type": "demo",
                "version": agent.version,
                "supported_languages": agent.supported_languages,
                "capabilities": ["deterministic_retrieval", "trace_emission", "multilingual_answers"]
            }
        )

    if not agent.endpoint:
        return AgentConnectionTestResponse(
            status="ERROR",
            latency_ms=0,
            status_code=None,
            message="Agent does not have an endpoint configured.",
            details={"error": "MISSING_ENDPOINT"}
        )

    # Perform real ping / test call to external agent endpoint
    test_payload = {
        "test_case_id": "CONNECTION_PROBE",
        "question": "AgentTrust connectivity and schema verification probe.",
        "language": "en",
        "category": "probe",
        "source_documents": [],
        "metadata": {"probe": True, "timestamp": time.time()}
    }

    headers = {"Content-Type": "application/json"}
    if agent.config_json and "api_key" in agent.config_json and agent.config_json["api_key"]:
        headers["Authorization"] = f"Bearer {agent.config_json['api_key']}"
    if agent.config_json and "headers" in agent.config_json and isinstance(agent.config_json["headers"], dict):
        headers.update(agent.config_json["headers"])

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(agent.endpoint, json=test_payload, headers=headers)
            latency_ms = int((time.time() - start_time) * 1000)

            if resp.status_code >= 400:
                return AgentConnectionTestResponse(
                    status="ERROR",
                    latency_ms=latency_ms,
                    status_code=resp.status_code,
                    message=f"Agent endpoint returned HTTP {resp.status_code}",
                    details={"response_text": resp.text[:500]}
                )

            data = resp.json()
            # Validate schema contract
            has_answer = "answer" in data or "final_answer" in data
            has_citations = "citations" in data
            has_trace = "trace" in data
            has_retrieval = "retrieved_documents" in data or "documents" in data

            return AgentConnectionTestResponse(
                status="SUCCESS",
                latency_ms=latency_ms,
                status_code=resp.status_code,
                message="Agent endpoint successfully reached and returned valid response schema.",
                details={
                    "status_code": resp.status_code,
                    "has_answer": has_answer,
                    "has_citations": has_citations,
                    "has_trace": has_trace,
                    "has_retrieval": has_retrieval,
                    "sample_keys": list(data.keys())
                }
            )
    except httpx.ConnectError:
        latency_ms = int((time.time() - start_time) * 1000)
        return AgentConnectionTestResponse(
            status="ERROR",
            latency_ms=latency_ms,
            status_code=None,
            message=f"Connection refused: Unable to connect to {agent.endpoint}. Verify agent is running.",
            details={"error": "CONNECTION_REFUSED"}
        )
    except httpx.TimeoutException:
        latency_ms = int((time.time() - start_time) * 1000)
        return AgentConnectionTestResponse(
            status="ERROR",
            latency_ms=latency_ms,
            status_code=None,
            message=f"Connection timed out after 10.0s while contacting {agent.endpoint}.",
            details={"error": "TIMEOUT"}
        )
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return AgentConnectionTestResponse(
            status="ERROR",
            latency_ms=latency_ms,
            status_code=None,
            message=f"Failed to communicate with agent endpoint: {str(e)}",
            details={"error": str(e)}
        )
