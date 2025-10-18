from fastapi import APIRouter
from sqlmodel import select

from otoge_service.models import OngekiSkill
from otoge_service.sessions import async_session_ctx

router = APIRouter()


@router.get("/skills", response_model=list[OngekiSkill])
async def get_ongeki_skills(
    id: int | None = None,
    type: str | None = None,
):
    async with async_session_ctx() as session:
        clause = select(OngekiSkill)
        if id is not None:
            clause = clause.where(OngekiSkill.id == id)
        if type is not None:
            clause = clause.where(OngekiSkill.type == type)
        return (await session.exec(clause)).all()
