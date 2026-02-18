from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from .base_model import Base


class Player(Base):
    __tablename__ = "Players"  # Имя таблицы в MySQL

    # Поле ID (первичный ключ, создается автоматически)
    id: Mapped[int] = mapped_column("ID", primary_key=True)

    # Имя игрока (строка, не может быть пустой)
    name: Mapped[str] = mapped_column("Name", String(255), index=True, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}')>"