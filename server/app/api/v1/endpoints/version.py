"""Version endpoint for CodeAtlas Server."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/version", summary="Get service version information")
async def get_version():
    """Returns the current service name, version, and build info."""
    return {
        "service": "CodeAtlas Server",
        "version": "0.10.5",
        "build": "development",
    }
