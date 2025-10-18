from maimai_py import MaimaiRoutes

from otoge_service.providers.usagicard import UsagiCardProvider


def get_router(routes: MaimaiRoutes):
    return routes.get_updates_chain_route(
        source_deps=[
            ("divingfish", routes._dep_divingfish),
            ("lxns", routes._dep_lxns),
            ("wechat", routes._dep_wechat),
            ("arcade", routes._dep_arcade),
        ],
        target_deps=[
            ("divingfish", routes._dep_divingfish),
            ("lxns", routes._dep_lxns),
            ("usagicard", lambda: UsagiCardProvider()),
        ],
        source_mode="fallback",
        target_mode="parallel",
    )
