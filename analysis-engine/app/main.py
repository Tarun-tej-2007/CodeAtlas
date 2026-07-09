from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="CodeAtlas Analysis Engine",
    description="Analysis service for CodeAtlas",
    version="1.0.0",
)

app.include_router(api_router)