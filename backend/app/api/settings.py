import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.api.deps import get_optional_user, log_audit_event

router = APIRouter(prefix="/settings", tags=["Settings"])


class ProviderSettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None
    translation_provider: Optional[str] = None


@router.get("/provider")
async def get_provider_settings():
    """
    Returns provider configuration safely. Never returns raw secret API keys.
    """
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "llm_base_url": settings.LLM_BASE_URL,
        "llm_api_key_configured": bool(settings.LLM_API_KEY and len(settings.LLM_API_KEY) > 0),
        "translation_provider": settings.TRANSLATION_PROVIDER,
        "max_concurrency": settings.MAX_CONCURRENCY,
        "evaluation_timeout_sec": settings.EVALUATION_TIMEOUT_SEC,
        "supported_languages": ["en", "kn", "hi", "te"],
    }


@router.post("/provider")
async def update_provider_settings(
    req: ProviderSettingsUpdate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Updates provider configurations safely.
    """
    if req.llm_provider:
        settings.LLM_PROVIDER = req.llm_provider
    if req.llm_model:
        settings.LLM_MODEL = req.llm_model
    if req.llm_base_url:
        settings.LLM_BASE_URL = req.llm_base_url
    if req.llm_api_key is not None and req.llm_api_key.strip():
        settings.LLM_API_KEY = req.llm_api_key.strip()
    if req.translation_provider:
        settings.TRANSLATION_PROVIDER = req.translation_provider

    if current_user:
        await log_audit_event(
            db=db,
            action="PROVIDER_SETTINGS_UPDATED",
            entity_type="settings",
            user_id=current_user.id,
            details={
                "llm_provider": settings.LLM_PROVIDER,
                "llm_model": settings.LLM_MODEL,
                "api_key_updated": bool(req.llm_api_key and req.llm_api_key.strip())
            }
        )

    return {
        "message": "Provider settings updated successfully.",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "llm_api_key_configured": bool(settings.LLM_API_KEY and len(settings.LLM_API_KEY) > 0)
    }
