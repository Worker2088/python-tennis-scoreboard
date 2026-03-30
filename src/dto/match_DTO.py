from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, NamedTuple, Self
import re

from sqlalchemy import Boolean

from src.dto.score_DTO import MatchScoreDTO

class MatchCreateDTO(BaseModel):
    player_one_name: str
    player_two_name: str

    @field_validator("player_one_name", "player_two_name")
    @classmethod
    def validate_name_chars(cls, value: str) -> str:
        # Регулярное выражение:
        # ^[а-яА-ЯёЁa-zA-Z\s\-]+$
        # (Кириллица, латиница, пробелы, дефисы от начала до конца строки)
        pattern = r"^[а-яА-ЯёЁa-zA-Z\s\-]{2,20}$"
        if not re.match(pattern, value):
            raise ValueError(
                "Имя может содержать только буквы (рус/лат), пробелы и дефисы, длинна от 2 до 20 симв"
            )
        return value.strip()  # Убираем лишние пробелы по краям

    @model_validator(mode="after")
    def check_names_are_different(self) -> Self:
        # Здесь мы уже имеем доступ к ОБОИМ полям через self
        if self.player_one_name.lower() == self.player_two_name.lower():
            raise ValueError("Игроки должны иметь разные имена")
        return self


class MatchDTO(BaseModel):
    id: int
    uuid: str
    player_one_name: str
    player_two_name: str
    winner_id: int | None
    score: MatchScoreDTO = Field(default_factory=MatchScoreDTO)

    model_config = ConfigDict(from_attributes=True)

class MatchDisplayDTO(BaseModel):
    player_one_name: str
    player_two_name: str
    winner_name: str
    is_error_name: bool = False

class PaginatedMatches(NamedTuple):
    matches: List[MatchDisplayDTO]
    filter_by_player_name: str
    total_pages: int
    current_page: int
    has_next: bool
    has_prev: bool

    # model_config = ConfigDict(from_attributes=True)



