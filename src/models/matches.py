"""
Модуль содержит описание модели Match в базе данных.

Хранит информацию о UUID, игроках, победителе и текущем счете.
"""
import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class MatchModel(Base):
    """
    Модель теннисного матча в базе данных.

    Attributes:
        id (int): Уникальный идентификатор матча.
        uuid (str): Уникальный идентификатор матча в формате UUID.
        player_one_id (int): ID первого игрока.
        player_two_id (int): ID второго игрока.
        winner_id (int | None): ID победителя (если матч завершен).
        score (dict[str, Any]): Счет матча в формате JSON.
    """
    __tablename__ = "Matches"

    id: Mapped[int] = mapped_column("ID", primary_key=True)

    # 2. Добавляем поле UUID
    uuid: Mapped[str] = mapped_column("UUID",
        String(36),                         # Длина UUID всегда 36 символов
        unique=True,                        # Делаем его уникальным
        nullable=False,                     # Поле не может быть пустым
        default=lambda: str(uuid.uuid4())   # Автоматическая генерация при создании
    )

    # Внешние ключи: связываем матч с ID игроков из таблицы players
    player_one_id: Mapped[int] = mapped_column("Player1", ForeignKey("Players.ID"))
    player_two_id: Mapped[int] = mapped_column("Player2", ForeignKey("Players.ID"))

    # Победитель (может быть пустым, пока матч идет)
    winner_id: Mapped[int | None] = mapped_column("Winner", ForeignKey("Players.ID"), nullable=True)

    score: Mapped[dict[str, Any]] = mapped_column("Score", JSON, nullable=True)

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта матча.

        Returns:
            str: Строка с информацией о матче.
        """
        # Безопасно берем срез UUID, если он не None
        short_uuid = self.uuid[:8] if self.uuid else "None"

        return (
            f"<Match(id={self.id}, "
            f"uuid='{short_uuid}...', "
            f"p1={self.player_one_id}, "
            f"p2={self.player_two_id}, "
            f"winner={self.winner_id}, "
            f"score='{self.score}')>"
        )