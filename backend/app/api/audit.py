from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.api.deps import get_optional_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    workspace_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    query = select(AuditLog)
    if workspace_id:
        query = query.where(AuditLog.workspace_id == workspace_id)
    if action:
        query = query.where(AuditLog.action == action)
    query = query.order_by(AuditLog.created_at.desc()).limit(limit)

    result = await db.execute(query)
    entries = result.scalars().all()
    return [AuditLogResponse.model_validate(e) for e in entries]
