from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "service": "CodeAtlas Analysis Engine",
        "status": "running"
    }