from fastapi import APIRouter

from otoge_service.routes.chunithm import characters
from otoge_service.settings import get_settings

router = APIRouter()
settings = get_settings()

if settings.enable_chunithm_assets:
    router.include_router(characters.router)
