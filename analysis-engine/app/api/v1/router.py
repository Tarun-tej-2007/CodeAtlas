from fastapi import APIRouter
from app.api.v1.endpoints import health, analyze, version

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    version.router,
    prefix="/api/v1",
    tags=["Version"]
)

api_router.include_router(
    analyze.router,
    prefix="/api/v1",
    tags=["Analysis"]
)