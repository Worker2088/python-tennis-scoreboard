import uuid # 1. Импортируем стандартный модуль Python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import Base


class Match(Base):
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

    # Счет матча (например, "6:4, 7:5")
    score: Mapped[str | None] = mapped_column("Score", String(5), default="0:0")