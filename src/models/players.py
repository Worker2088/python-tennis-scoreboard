"""
Модуль содержит описание модели Player в базе данных.

Хранит имена игроков с уникальным индексом.
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import Base


class Player(Base):
    """
    Модель игрока в базе данных.

    Attributes:
        id (int): Уникальный идентификатор игрока.
        name (str): Имя игрока.
    """
    __tablename__ = "Players"  # Имя таблицы в MySQL

    # Поле ID (первичный ключ, создается автоматически)
    id: Mapped[int] = mapped_column("ID", primary_key=True)

    # Имя игрока (строка, не может быть пустой)
    name: Mapped[str] = mapped_column("Name", String(255), index=True, nullable=False, unique=True)

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта игрока.

        Returns:
            str: Строка с ID и именем игрока.
        """
        return f"<Player(id={self.id}, name='{self.name}')>"