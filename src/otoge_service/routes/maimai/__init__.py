from fastapi import APIRouter
from maimai_py import MaimaiRoutes, PlayerIdentifier

from otoge_service.providers.usagicard import UsagiCardProvider
from otoge_service.routes.maimai import chains, characters
from otoge_service.sessions import maimai_client
from otoge_service.settings import get_settings

router = APIRouter()
settings = get_settings()

routes = MaimaiRoutes(
    maimai_client,
    settings.lxns_developer_token,
    settings.divingfish_developer_token,
    settings.arcade_proxy,
)

if settings.enable_maimai_assets:
    router.include_router(routes.get_router(routes._dep_hybrid, skip_base=False))
    router.include_router(characters.router)  # add maimai characters route (next to the included base routes)
router.include_router(chains.get_router(routes))  # add maimai update chain route
router.include_router(routes.get_router(routes._dep_divingfish, routes._dep_divingfish_player), prefix="/divingfish")
router.include_router(routes.get_router(routes._dep_lxns, routes._dep_lxns_player), prefix="/lxns")
router.include_router(routes.get_router(routes._dep_wechat, routes._dep_wechat_player), prefix="/wechat")
router.include_router(routes.get_router(routes._dep_arcade, routes._dep_arcade_player), prefix="/arcade")
router.include_router(routes.get_router(lambda: UsagiCardProvider(), lambda uuid: PlayerIdentifier(credentials=uuid)), prefix="/usagicard")
