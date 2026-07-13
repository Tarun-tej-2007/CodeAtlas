from fastapi import APIRouter

from app.api.v1.endpoints import health, auth

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)