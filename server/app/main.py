from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="CodeAtlas API",
    description="Backend API for CodeAtlas",
    version="1.0.0",
)

app.include_router(api_router)