from fastapi import APIRouter
from sqlmodel import col, select

from otoge_service.models import ChunithmCharacter
from otoge_service.sessions import async_session_ctx

router = APIRouter()


@router.get("/characters", response_model=list[ChunithmCharacter])
async def get_chunithm_characters(
    id: int | None = None,
    name: str | None = None,
):
    async with async_session_ctx() as session:
        clause = select(ChunithmCharacter)
        if id is not None:
            clause = clause.where(ChunithmCharacter.id == id)
        if name is not None:
            clause = clause.where(col(ChunithmCharacter.name).ilike(f"%{name}%"))
        return (await session.exec(clause)).all()
