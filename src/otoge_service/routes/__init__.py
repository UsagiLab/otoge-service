from fastapi import APIRouter

from otoge_service import sessions
from otoge_service.routes import chunithm, developers, maimai, ongeki

router = APIRouter()
settings = sessions.get_settings()

router.include_router(maimai.router, prefix="/maimai", tags=["maimai"], dependencies=developers.dependencies)
router.include_router(ongeki.router, prefix="/ongeki", tags=["ongeki"], dependencies=developers.dependencies)
router.include_router(chunithm.router, prefix="/chunithm", tags=["chunithm"], dependencies=developers.dependencies)
if settings.enable_developer_apply and settings.enable_developer_check:
    router.include_router(developers.router, prefix="/developers", tags=["developers"])
