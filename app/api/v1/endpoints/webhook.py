from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def bot_health():
    return {"bot": "connected"}
