import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.api.deps import get_current_user, log_audit_event

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == current_user.id)
        .order_by(Workspace.created_at.desc())
    )
    result = await db.execute(query)
    workspaces = result.scalars().all()
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    req: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    slug_base = re.sub(r"[^a-z0-9]", "-", req.name.lower().strip()) or "workspace"
    import uuid
    workspace_slug = f"{slug_base}-{str(uuid.uuid4())[:6]}"

    workspace = Workspace(
        name=req.name.strip(),
        slug=workspace_slug,
        owner_id=current_user.id
    )
    db.add(workspace)
    await db.flush()

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    await db.flush()

    await log_audit_event(
        db=db,
        action="WORKSPACE_CREATED",
        entity_type="workspace",
        entity_id=workspace.id,
        user_id=current_user.id,
        workspace_id=workspace.id,
        details={"name": workspace.name}
    )

    return WorkspaceResponse.model_validate(workspace)
