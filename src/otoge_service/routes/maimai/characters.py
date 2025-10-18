from fastapi import APIRouter
from sqlmodel import col, select

from otoge_service import sessions
from otoge_service.models import MaimaiCharacter
from otoge_service.sessions import async_session_ctx

router = APIRouter()
settings = sessions.get_settings()


@router.get("/characters", response_model=list[MaimaiCharacter])
async def get_maimai_characters(
    id: int | None = None,
    name: str | None = None,
):
    async with async_session_ctx() as session:
        clause = select(MaimaiCharacter)
        if id is not None:
            clause = clause.where(MaimaiCharacter.id == id)
        if name is not None:
            clause = clause.where(col(MaimaiCharacter.name).ilike(f"%{name}%"))
        return (await session.exec(clause)).all()
