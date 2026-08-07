from fastapi import APIRouter
from app.api.v1.endpoints import health, analyze, version, incremental, evolution, governance, decision

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

api_router.include_router(
    incremental.router,
    prefix="/api/v1",
    tags=["Incremental Analysis"]
)

api_router.include_router(
    evolution.router,
    prefix="/api/v1",
    tags=["Architecture Evolution"]
)

api_router.include_router(
    governance.router,
    prefix="/api/v1",
    tags=["Architecture Governance"]
)

api_router.include_router(
    decision.router,
    prefix="/api/v1",
    tags=["Architecture Decision Intelligence"]
)