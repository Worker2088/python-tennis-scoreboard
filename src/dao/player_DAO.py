import sqlite3
from logging import getLogger
from pathlib import Path
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.players import Player

logger = getLogger(__name__)

class PlayerDAO:
    def __init__(self, session: Session):
        # Сессия — это наше "окно" в базу данных
        self.session = session

    def add_player(self, name: str) -> Player:
        # Создаем "черновик" объекта
        new_player = Player(name=name)
        # Кладем его на стол архивариусу
        self.session.add(new_player)
        # Сохраняем изменения в реальную базу данных
        self.session.commit()
        # Обновляем объект, чтобы получить его ID из базы
        self.session.refresh(new_player)
        return new_player


    def select_by_name(self, name: str) -> Optional[Player]:
        """
        Ищет игрока в базе данных по его имени.
        """
        # 1. Создаем запрос: "Выбери игрока, чье имя совпадает с переданным"
        query = select(Player).where(Player.name == name)

        # 2. Выполняем запрос и просим вернуть ОДИН результат или None
        # .scalar() вытаскивает сам объект Player из обертки результата
        result = self.session.execute(query).scalar_one_or_none()

        return result

    def select_by_id(self, id: int) -> Optional[Player]:
        """
        Ищет игрока в базе данных по его имени.
        """
        # 1. Создаем запрос: "Выбери игрока, чье имя совпадает с переданным"
        query = select(Player).where(Player.id == id)

        # 2. Выполняем запрос и просим вернуть ОДИН результат или None
        # .scalar() вытаскивает сам объект Player из обертки результата
        result = self.session.execute(query).scalar_one_or_none()

        return result

