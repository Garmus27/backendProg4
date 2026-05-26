from fastapi import APIRouter
from sqlmodel import text
from app.core.database import engine

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    return {"status": "ok"}
