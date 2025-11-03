import asyncio
import re
import typing
from collections import defaultdict
from typing import TypeVar

from fastapi import HTTPException, status
from maimai_py import IScoreProvider, IScoreUpdateProvider, MaimaiClient, PlayerIdentifier, Song
from maimai_py.models import Score as MpyScore
from sqlmodel import col, select

from otoge_service.exceptions import LeporidException
from otoge_service.models import Score
from otoge_service.sessions import async_session_ctx

T = TypeVar("T")
score_update_lock = defaultdict(asyncio.Lock)

uuid_pattern = re.compile(r"^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$", re.IGNORECASE)


class UsagiCardProvider(IScoreProvider, IScoreUpdateProvider):
    def _check_uuid(self, identifier: PlayerIdentifier) -> str:
        assert isinstance(identifier.credentials, str), "Identifier credentials must be a string"
        if not uuid_pattern.match(identifier.credentials):
            raise LeporidException.INVALID_CREDENTIALS.msg("无效的 UUID 格式")
        return identifier.credentials

    async def get_scores_all(self, identifier: PlayerIdentifier, client: MaimaiClient) -> list[MpyScore]:
        uuid_ident = self._check_uuid(identifier)
        async with async_session_ctx() as session:
            stmt = select(Score).where(col(Score.uuid) == uuid_ident)
            return [score.as_mpy() for score in await session.exec(stmt)]

    async def get_scores_one(self, identifier: PlayerIdentifier, song: Song, client: MaimaiClient) -> list[MpyScore]:
        uuid_ident = self._check_uuid(identifier)
        async with async_session_ctx() as session:
            stmt = select(Score).where(col(Score.uuid) == uuid_ident, col(Score.song_id) % 10000 == song.id)
            return [score.as_mpy() for score in await session.exec(stmt)]

    async def update_scores(self, identifier: PlayerIdentifier, scores: typing.Iterable[MpyScore], client: MaimaiClient) -> None:
        uuid_ident = self._check_uuid(identifier)
        async with async_session_ctx() as session, score_update_lock[identifier.credentials]:
            stmt = select(Score).where(col(Score.uuid) == uuid_ident).with_for_update()
            old_scores = {f"{s.song_id} {s.type} {s.level_index}": s for s in await session.exec(stmt)}
            for new_score in scores:
                score_key = f"{new_score.id} {new_score.type} {new_score.level_index}"
                if score_key in old_scores:
                    # score already exists in the database, merge the score
                    old_scores[score_key].merge_mpy(new_score)
                else:
                    # score does not exist in the database, add the score
                    session.add(Score.from_mpy(new_score, uuid_ident))
            await session.commit()
