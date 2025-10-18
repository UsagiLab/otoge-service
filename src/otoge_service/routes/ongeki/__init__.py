from fastapi import APIRouter

from otoge_service.routes.ongeki import cards, skills
from otoge_service.settings import get_settings

router = APIRouter()
settings = get_settings()

if settings.enable_ongeki_assets:
    router.include_router(cards.router)
    router.include_router(skills.router)
