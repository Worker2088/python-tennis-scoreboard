"""
Модуль содержит объекты передачи данных (DTO), связанных с матчами.

Использует Pydantic для валидации имен игроков и пагинации списка.
"""
import re
from typing import List, NamedTuple, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.dto.score_DTO import MatchScoreDTO

class MatchCreateDTO(BaseModel):
    """
    DTO для создания нового матча.

    Attributes:
        player_one_name (str): Имя первого игрока.
        player_two_name (str): Имя второго игрока.
    """
    player_one_name: str
    player_two_name: str

    @field_validator("player_one_name", "player_two_name")
    @classmethod
    def validate_name_chars(cls, value: str) -> str:
        """
        Проверяет корректность имени игрока (длина и допустимые символы).

        Args:
            value (str): Проверяемое имя.

        Returns:
            str: Очищенное имя.

        Raises:
            ValueError: Если имя не соответствует формату.
        """
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
        """
        Проверяет, что имена игроков различаются.

        Returns:
            Self: Объект DTO после валидации.

        Raises:
            ValueError: Если имена игроков одинаковы.
        """
        if self.player_one_name.lower() == self.player_two_name.lower():
            raise ValueError("Игроки должны иметь разные имена")
        return self


class MatchDTO(BaseModel):
    """
    DTO для представления полной информации о матче.

    Attributes:
        id (int): ID матча.
        uuid (str): UUID матча.
        player_one_name (str): Имя первого игрока.
        player_two_name (str): Имя второго игрока.
        winner_id (int | None): ID победителя.
        score (MatchScoreDTO): Счет матча.
    """
    id: int
    uuid: str
    player_one_name: str
    player_two_name: str
    winner_id: int | None
    score: MatchScoreDTO = Field(default_factory=MatchScoreDTO)

    model_config = ConfigDict(from_attributes=True)

class MatchDisplayDTO(BaseModel):
    """
    DTO для отображения информации о матче в списке.

    Attributes:
        player_one_name (str): Имя первого игрока.
        player_two_name (str): Имя второго игрока.
        winner_name (str): Имя победителя.
        is_error_name (bool): Флаг ошибки в имени.
    """
    player_one_name: str
    player_two_name: str
    winner_name: str
    is_error_name: bool = False

class PaginatedMatches(NamedTuple):
    """
    Результат пагинации списка матчей.

    Attributes:
        matches (List[MatchDisplayDTO]): Список матчей на странице.
        filter_by_player_name (str): Примененный фильтр по имени.
        total_pages (int): Общее количество страниц.
        current_page (int): Текущая страница.
        has_next (bool): Есть ли следующая страница.
        has_prev (bool): Есть ли предыдущая страница.
    """
    matches: List[MatchDisplayDTO]
    filter_by_player_name: str
    total_pages: int
    current_page: int
    has_next: bool
    has_prev: bool




