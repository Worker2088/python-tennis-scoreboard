"""
Модуль содержит объект доступа к данным (DAO) для игроков.

Реализует поиск игроков в базе данных и добавление новых.
"""
from logging import getLogger

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.players import Player

logger = getLogger(__name__)

class PlayerDAO:
    """
    Класс для доступа к данным игроков в базе данных (Data Access Object).
    """
    def __init__(self, session: Session) -> None:
        """
        Инициализирует DAO сессией базы данных.

        Args:
            session (Session): Сессия SQLAlchemy.
        """
        # Сессия — это наше "окно" в базу данных
        self.session = session

    def create(self, name: str) -> Player:
        """
        Создает и сохраняет нового игрока в базе данных.

        Args:
            name (str): Имя нового игрока.

        Returns:
            Player: Созданный объект игрока с заполненным ID.
        """
        # Создаем "черновик" объекта
        new_player = Player(name=name)
        # Кладем его на стол архивариусу
        self.session.add(new_player)
        # Сохраняем изменения в реальную базу данных
        self.session.commit()
        # Обновляем объект, чтобы получить его ID из базы
        self.session.refresh(new_player)
        return new_player

    def get_by_name(self, name: str) -> Player | None:
        """
        Ищет игрока в базе данных по его имени.

        Args:
            name (str): Имя игрока для поиска.

        Returns:
            Player | None: Объект игрока или None, если не найден.
        """
        # 1. Создаем запрос: "Выбери игрока, чье имя совпадает с переданным"
        query = select(Player).where(Player.name == name)

        # 2. Выполняем запрос и просим вернуть ОДИН результат или None
        # .scalar() вытаскивает сам объект Player из обертки результата
        result = self.session.execute(query).scalar_one_or_none()

        return result

    def get_by_id(self, id: int) -> Player | None:
        """
        Ищет игрока в базе данных по его идентификатору.

        Args:
            id (int): ID игрока для поиска.

        Returns:
            Player | None: Объект игрока или None, если не найден.
        """
        # 1. Создаем запрос: "Выбери игрока, чье имя совпадает с переданным"
        query = select(Player).where(Player.id == id)

        # 2. Выполняем запрос и просим вернуть ОДИН результат или None
        # .scalar() вытаскивает сам объект Player из обертки результата
        result = self.session.execute(query).scalar_one_or_none()

        return result

