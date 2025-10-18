from fastapi import APIRouter
from sqlmodel import col, select

from otoge_service.models import OngekiCard
from otoge_service.sessions import async_session_ctx

router = APIRouter()


@router.get("/cards", response_model=list[OngekiCard])
async def get_ongeki_cards(
    id: int | None = None,
    name: str | None = None,
    character_name: str | None = None,
    rarity: str | None = None,
    attribute: str | None = None,
):
    async with async_session_ctx() as session:
        clause = select(OngekiCard)
        if id is not None:
            clause = clause.where(OngekiCard.id == id)
        if name is not None:
            clause = clause.where(col(OngekiCard.name).ilike(f"%{name}%"))
        if character_name is not None:
            clause = clause.where(col(OngekiCard.character_name).ilike(f"%{character_name}%"))
        if rarity is not None:
            clause = clause.where(OngekiCard.rarity == rarity)
        if attribute is not None:
            clause = clause.where(OngekiCard.attribute == attribute)
        return (await session.exec(clause)).all()
