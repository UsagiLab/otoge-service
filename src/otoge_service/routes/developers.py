import secrets

from fastapi import APIRouter, Depends, Security
from fastapi.security import APIKeyHeader
from sqlmodel import select

from otoge_service import sessions
from otoge_service.exceptions import LeporidException
from otoge_service.models import Developer
from otoge_service.sessions import async_session_ctx

router = APIRouter()
settings = sessions.get_settings()
api_key_header = APIKeyHeader(name="x-developer-token", auto_error=False)


async def require_developer_token(api_key: str | None = Security(api_key_header)):
    if api_key is not None:
        if api_key in sessions.enabled_developer_tokens:
            return api_key
        raise LeporidException.INVALID_CREDENTIALS.msg("开发者令牌无效")
    raise LeporidException.INVALID_CREDENTIALS.msg("需要提供开发者令牌")


dependencies = []
if settings.enable_developer_check:
    dependencies.append(Depends(require_developer_token))


@router.post("", response_model=Developer)
async def apply_developer(name: str, description: str | None = None):
    async with async_session_ctx() as session:
        token = secrets.token_hex(16)
        developer = Developer(name=name, token=token, description=description, enabled=False)
        session.add(developer)
        await session.commit()
    return developer


@router.get("", response_model=Developer)
async def get_developer(developer_token: str):
    await sessions.init_developers()
    async with async_session_ctx() as session:
        developer = (await session.exec(select(Developer).where(Developer.token == developer_token))).first()
        return developer
    raise LeporidException.INVALID_CREDENTIALS.msg("开发者令牌无效")
