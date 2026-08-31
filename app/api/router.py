from fastapi import APIRouter
from app.api.endpoints import audio

api_router = APIRouter()
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
