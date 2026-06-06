from fastapi import APIRouter

from jober_api.routers.exports import router as exports_router
from jober_api.routers.imports import router as imports_router
from jober_api.routers.job_targets import router as job_targets_router

api_router = APIRouter(prefix="/api")
api_router.include_router(imports_router)
api_router.include_router(exports_router)
api_router.include_router(job_targets_router)
