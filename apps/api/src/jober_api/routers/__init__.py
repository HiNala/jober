from fastapi import APIRouter

from jober_api.routers.batches import router as batches_router
from jober_api.routers.documents import router as documents_router
from jober_api.routers.exports import router as exports_router
from jober_api.routers.form_discovery import router as form_discovery_router
from jober_api.routers.form_fill import router as form_fill_router
from jober_api.routers.imports import router as imports_router
from jober_api.routers.job_extraction import router as job_extraction_router
from jober_api.routers.job_targets import router as job_targets_router
from jober_api.routers.profile import router as profile_router
from jober_api.routers.recovery import router as recovery_router
from jober_api.routers.resumes import router as resumes_router
from jober_api.routers.run_console import router as run_console_router
from jober_api.routers.verification import router as verification_router

api_router = APIRouter(prefix="/api")
api_router.include_router(imports_router)
api_router.include_router(exports_router)
api_router.include_router(job_targets_router)
api_router.include_router(job_extraction_router)
api_router.include_router(profile_router)
api_router.include_router(resumes_router)
api_router.include_router(documents_router)
api_router.include_router(form_discovery_router)
api_router.include_router(form_fill_router)
api_router.include_router(verification_router)
api_router.include_router(recovery_router)
api_router.include_router(run_console_router)
api_router.include_router(batches_router)
