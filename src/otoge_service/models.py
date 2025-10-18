from datetime import datetime
from decimal import Decimal
from typing import Self

from maimai_py import Score as MpyScore
from maimai_py.models import FCType, FSType, LevelIndex, RateType, SongType
from sqlmodel import Field, SQLModel


class Score(SQLModel, table=True):
    __tablename__ = "tbl_score"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    song_id: int = Field(index=True)
    level_index: LevelIndex
    achievements: Decimal = Field(default=None, max_digits=7, decimal_places=4)
    dx_score: int
    dx_rating: float
    play_count: int
    fc: FCType | None
    fs: FSType | None
    rate: RateType
    type: SongType
    uuid: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def from_mpy(mpy_score: MpyScore, uuid: str):
        return Score(
            song_id=mpy_score.id,
            level_index=mpy_score.level_index,
            achievements=Decimal(mpy_score.achievements or 0),
            fc=mpy_score.fc,
            fs=mpy_score.fs,
            dx_score=mpy_score.dx_score or 0,
            dx_rating=mpy_score.dx_rating or 0,
            play_count=mpy_score.play_count or 0,
            rate=mpy_score.rate,
            type=mpy_score.type,
            uuid=uuid,
        )

    def as_mpy(self) -> MpyScore:
        return MpyScore(
            id=self.song_id,
            level="Unknown",
            level_index=self.level_index,
            achievements=float(self.achievements),
            fc=self.fc,
            fs=self.fs,
            dx_score=self.dx_score,
            dx_rating=self.dx_rating,
            play_time=None,
            play_count=self.play_count,
            rate=self.rate,
            type=self.type,
        )

    def merge_mpy(self, new: MpyScore | None) -> Self:
        if new is not None:
            if self.song_id != new.id or self.level_index != new.level_index or self.type != new.type:
                raise ValueError("Cannot join scores with different songs, level indexes or types")
            selected_value = None
            if self.achievements != new.achievements:
                selected_value = Decimal(max(self.achievements or 0, new.achievements or 0))
                self.achievements = selected_value
            if self.dx_rating != new.dx_rating and new.dx_rating is not None:
                # theoretically, this should be trigger only when level_value changes or better score is achieved
                selected_value = new.dx_rating
                self.dx_rating = selected_value
            if self.dx_score != new.dx_score:
                selected_value = max(self.dx_score or 0, new.dx_score or 0)
                self.dx_score = selected_value
            if self.fc != new.fc:
                self_fc = self.fc.value if self.fc is not None else 100
                other_fc = new.fc.value if new.fc is not None else 100
                selected_value = min(self_fc, other_fc)
                self.fc = FCType(selected_value) if selected_value != 100 else None
            if self.fs != new.fs:
                self_fs = self.fs.value if self.fs is not None else -1
                other_fs = new.fs.value if new.fs is not None else -1
                selected_value = max(self_fs, other_fs)
                self.fs = FSType(selected_value) if selected_value != -1 else None
            if self.rate != new.rate:
                selected_value = min(self.rate.value, new.rate.value)
                self.rate = RateType(selected_value)
            if self.play_count != new.play_count:
                selected_value = max(self.play_count or 0, new.play_count or 0)
                self.play_count = selected_value
            if selected_value is not None:
                self.updated_at = datetime.utcnow()
        return self


class Developer(SQLModel, table=True):
    __tablename__ = "tbl_developer"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    token: str = Field(unique=True, index=True)
    description: str | None = Field(default=None)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Maimai Assets


class MaimaiCharacter(SQLModel, table=True):
    __tablename__ = "tbl_maimai_characters"  # type: ignore

    id: int = Field(primary_key=True, description="角色ID")
    name: str = Field(description="角色名")
    version: str = Field(description="版本")


class OngekiCard(SQLModel, table=True):
    __tablename__ = "tbl_ongeki_cards"  # type: ignore

    id: int = Field(primary_key=True, description="卡片ID")
    name: str = Field(description="卡片名")
    character_id: int = Field(default=1000, description="角色ID")
    character_name: str = Field(description="角色名")
    rarity: str = Field(description="稀有度")
    attribute: str = Field(description="属性")
    description: str | None = Field(default=None, description="称号")
    representative: str = Field(default=None, description="代表")
    grade_id: int = Field(default=2, description="年级ID")
    grade: str | None = Field(default=None, description="年级")
    group_id: int = Field(default=1, description="组合ID")
    group: str | None = Field(default=None, description="组合")
    skill_id: int = Field(default=100000, description="技能ID")
    skill: str = Field(description="技能")
    super_skill_id: int = Field(default=100041, description="超解花技能ID")
    super_skill: str = Field(description="超解花技能")
    version: str = Field(description="版本")
    version_number: str = Field(description="卡面数字")
    copyright: str | None = Field(default=None, description="版权名称")
    model_name: str | None = Field(default=None, description="3D模型名称")
    attack_power_0: int = Field(description="0星攻击力")
    attack_power_1: int = Field(description="1星攻击力")
    attack_power_2: int = Field(description="2星攻击力")
    attack_power_3: int = Field(description="3星攻击力")
    attack_power_4: int = Field(description="4星攻击力")
    attack_power_5: int = Field(description="5星攻击力")
    attack_power_7: int | None = Field(default=None, description="7星攻击力")
    attack_power_9: int | None = Field(default=None, description="9星攻击力")
    attack_power_11: int | None = Field(default=None, description="11星攻击力")
    attack_power_max: int = Field(description="MAX攻击力")


class OngekiSkill(SQLModel, table=True):
    __tablename__ = "tbl_ongeki_skills"  # type: ignore

    id: int = Field(primary_key=True, description="技能ID")
    type: str = Field(description="技能类型")
    details: str = Field(description="技能详细")


## Chunithm Models


class ChunithmCharacter(SQLModel, table=True):
    __tablename__ = "tbl_chunithm_characters"  # type: ignore

    id: int = Field(primary_key=True, description="角色ID")
    name: str = Field(description="角色名")
    rarity: int = Field(description="稀有度")
    tag_type: int = Field(description="标签种类")
    miss: int = Field(description="miss值")
    combo: int = Field(description="combo值")
    chain: int = Field(description="chain值")
    skill_name: str = Field(description="技能名")
    skill_description: str = Field(description="技能描述")
