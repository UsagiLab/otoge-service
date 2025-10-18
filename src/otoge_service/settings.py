from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="OTOGE_SERVICE_", case_sensitive=False)

    # application settings
    bind_host: str = "127.0.0.1"
    bind_port: int = 7100
    redis_url: str | None = None
    database_url: str = f"sqlite+aiosqlite:///database.db"

    # maimai.py settings
    lxns_developer_token: str | None = None
    divingfish_developer_token: str | None = None
    arcade_proxy: str | None = None

    # developer settings
    enable_developer_check: bool = False
    enable_developer_apply: bool = False

    # assets settings
    enable_maimai_assets: bool = False
    enable_ongeki_assets: bool = False
    enable_chunithm_assets: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
