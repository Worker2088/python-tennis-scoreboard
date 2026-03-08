import sqlite3
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Match
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased
from sqlalchemy import Row

from src.models.matches import MatchModel
from src.models.players import Player

logger = getLogger(__name__)

class MatchDAO:
    def __init__(self, session: Session):
        # Сессия — это наше "окно" в базу данных
        self.session = session

    def get_match_with_names(self, uuid: str) -> Row | None:
        # 1. Создаем "виртуальные копии" таблицы игроков
        p1 = aliased(Player)
        p2 = aliased(Player)

        # 2. Делаем ОДИН запрос, который склеивает Матч и двух Игроков
        return self.session.query(
            MatchModel,
            p1.name.label("p1_name"),
            p2.name.label("p2_name")
        ).join(p1, MatchModel.player_one_id == p1.id) \
            .join(p2, MatchModel.player_two_id == p2.id) \
            .filter(MatchModel.uuid == uuid) \
            .first()

    def get_all_matches(self, filter_by_player_name: str = None) -> list[Row] | None:
        # 1. Создаем "виртуальные копии" таблицы игроков
        p1 = aliased(Player)
        p2 = aliased(Player)
        win = aliased(Player)

        query = self.session.query(
            MatchModel,
            p1.name.label("p1_name"),
            p2.name.label("p2_name"),
            win.name.label("winner_name")
        ).join(p1, MatchModel.player_one_id == p1.id) \
            .join(p2, MatchModel.player_two_id == p2.id) \
            .join(win, MatchModel.winner_id == win.id)

        print('Match_DAO query', query)
        print('Match_DAO query all', query.all())
        # Реализуем фильтрацию, если имя передано
        # if filter_by_player_name:
        #     search = f"%{filter_by_player_name}%"
        #     query = query.filter(
        #         or_(
        #             p1.name.ilike(search),
        #             p2.name.ilike(search)
        #         )
        #     )

        return query.all()  # Возвращает List[Row]


        # # 2. Делаем ОДИН запрос, который склеивает Матч и двух Игроков
        # return self.session.query(
        #     MatchModel,
        #     p1.name.label("p1_name"),
        #     p2.name.label("p2_name"),
        #     win.name.label("winner")
        # ).join(p1, MatchModel.player_one_id == p1.id) \
        #     .join(p2, MatchModel.player_two_id == p2.id) \
        #     .join(win, MatchModel.winner_id == win.id) \
        #     .filter(MatchModel.winner_id != None) \
        #     .all()


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

        query = select(MatchModel).where(MatchModel.uuid == uuid)

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


