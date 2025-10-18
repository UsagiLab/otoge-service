import contextlib
from urllib.parse import unquote, urlparse

import httpx
from aiocache import RedisCache
from aiocache.serializers import PickleSerializer
from maimai_py import MaimaiClient
from maimai_py.utils.sentinel import UNSET
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from otoge_service.models import Developer
from otoge_service.settings import get_settings

settings = get_settings()

async_engine = create_async_engine(settings.database_url)
httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(None))

redis_backend = UNSET
if settings.redis_url:
    redis_url = urlparse(settings.redis_url)
    redis_backend = RedisCache(
        serializer=PickleSerializer(),
        endpoint=unquote(redis_url.hostname or "localhost"),
        port=redis_url.port or 6379,
        password=redis_url.password,
        db=int(unquote(redis_url.path).replace("/", "")),
    )
maimai_client = MaimaiClient(cache=redis_backend)

enabled_developer_tokens: set[str] = set()


@contextlib.asynccontextmanager
async def async_session_ctx():
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session


async def init_db():
    import otoge_service.models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def init_developers():
    async with async_session_ctx() as session:
        developers = await session.exec(select(Developer).where(Developer.enabled == True))
        global enabled_developer_tokens
        enabled_developer_tokens = set(dev.token for dev in developers.all() if dev.enabled)
