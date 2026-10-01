from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.exceptions import (
    AnalysisEngineError,
    AnalysisEngineConnectionError,
    AnalysisEngineTimeoutError,
    AnalysisEngineRequestError,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CodeAtlas API",
    description="Backend API for CodeAtlas",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AnalysisEngineError)
async def analysis_engine_exception_handler(request, exc):
    """Global handler mapping AnalysisEngineError exceptions to standardized API error models."""
    if isinstance(exc, AnalysisEngineConnectionError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        code = "SERVICE_UNAVAILABLE"
    elif isinstance(exc, AnalysisEngineTimeoutError):
        status_code = status.HTTP_504_GATEWAY_TIMEOUT
        code = "GATEWAY_TIMEOUT"
    elif isinstance(exc, AnalysisEngineRequestError):
        status_code = status.HTTP_400_BAD_REQUEST
        code = "BAD_REQUEST"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        code = "INTERNAL_SERVER_ERROR"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc),
                "details": None,
            }
        },
    )


app.include_router(api_router)