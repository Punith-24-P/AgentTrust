from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse
from app.agents.adapter import get_agent_adapter

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(data: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        project_id=data.project_id,
        name=data.name,
        description=data.description,
        adapter_type=data.adapter_type,
        endpoint=data.endpoint,
        version=data.version,
        model=data.model,
        supported_languages=data.supported_languages,
        config_json=data.config_json
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
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
