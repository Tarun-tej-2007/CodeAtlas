"""Version endpoint for CodeAtlas Analysis Engine."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/version", summary="Get service version information")
async def get_version():
    """Returns the current service name, version, and build info."""
    return {
        "service": "CodeAtlas Analysis Engine",
        "version": "0.10.5",
        "build": "development",
    }
