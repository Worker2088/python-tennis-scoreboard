import sqlite3
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Match
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.matches import MatchModel

logger = getLogger(__name__)

class MatchDAO:
    def __init__(self, session: Session):
        # Сессия — это наше "окно" в базу данных
        self.session = session

    def match_create(self, new_match: MatchModel) -> MatchModel:# object_model: Match) -> Match:
        # Создаем "черновик" объекта
        # new_match = MatchModel(player_one_id=player1_id, player_two_id=player2_id)
        # print('new_match_dao', new_match)
        # Кладем его на стол архивариусу
        self.session.add(new_match)
        # Сохраняем изменения в реальную базу данных
        self.session.commit()
        # Обновляем объект, чтобы получить его ID из базы
        self.session.refresh(new_match)
        print('new_match_dao_refresh', new_match)
        return new_match

    def select_by_uuid(self, uuid: str) -> Optional[MatchModel]:

        # 1. Создаем запрос: "Выбери игрока, чье имя совпадает с переданным"
        query = select(MatchModel).where(MatchModel.uuid == uuid)

        # 2. Выполняем запрос и просим вернуть ОДИН результат или None
        # .scalar() вытаскивает сам объект Player из обертки результата
        result = self.session.execute(query).scalar_one_or_none()

        return result

    # def get_all(self) -> List[CurrencyModel]:
    #     """
    #     Возвращает все валюты из базы данных.
    #     Returns:
    #         List[CurrencyModel]: Список моделей всех валют.
    #     """
    #     with sqlite3.connect(WEB_DIR_DB) as db:
    #         cursor = db.cursor()
    #         cursor.execute("SELECT id, FullName, Code, Sign FROM Currencies")
    #         all_currencies_tuples = cursor.fetchall()
    #         return [CurrencyModel(id=row[0], name=row[1], code=row[2], sign=row[3]) for row in all_currencies_tuples]
    #
    # def get_by_code(self, code: str) -> Optional[CurrencyModel]:
    #     """
    #     Находит одну валюту по ее коду.
    #     Args:
    #         code (str): Трехбуквенный код валюты.
    #     Returns:
    #         Optional[CurrencyModel]: Модель найденной валюты или None, если не найдена.
    #     """
    #     with sqlite3.connect(WEB_DIR_DB) as db:
    #         cursor = db.cursor()
    #         sql_query = "SELECT id, FullName, Code, Sign FROM Currencies WHERE Code = ?"
    #         cursor.execute(sql_query, (code.upper(),))
    #         row = cursor.fetchone()
    #         if row:
    #             return CurrencyModel(id=row[0], name=row[1], code=row[2], sign=row[3])
    #         return None


