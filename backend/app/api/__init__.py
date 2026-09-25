from fastapi import APIRouter
from app.api.projects import router as projects_router
from app.api.agents import router as agents_router
from app.api.datasets import router as datasets_router
from app.api.runs import router as runs_router
from app.api.reports import router as reports_router
from app.api.demo import router as demo_router

api_router = APIRouter(prefix="/api")
api_router.include_router(projects_router)
api_router.include_router(agents_router)
api_router.include_router(datasets_router)
api_router.include_router(runs_router)
api_router.include_router(reports_router)
api_router.include_router(demo_router)

__all__ = ["api_router"]
