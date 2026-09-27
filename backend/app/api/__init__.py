from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.workspaces import router as workspaces_router
from app.api.projects import router as projects_router
from app.api.agents import router as agents_router
from app.api.datasets import router as datasets_router
from app.api.evaluation_profiles import router as evaluation_profiles_router
from app.api.runs import router as runs_router
from app.api.reports import router as reports_router
from app.api.audit import router as audit_router
from app.api.settings import router as settings_router
from app.api.demo import router as demo_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(projects_router)
api_router.include_router(agents_router)
api_router.include_router(datasets_router)
api_router.include_router(evaluation_profiles_router)
api_router.include_router(runs_router)
api_router.include_router(reports_router)
api_router.include_router(audit_router)
api_router.include_router(settings_router)
api_router.include_router(demo_router)

__all__ = ["api_router"]
