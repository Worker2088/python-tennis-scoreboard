from ast import Index
from logging import getLogger
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy import Row
from src.services.exceptions import MatchNotFound

from src.models.matches import MatchModel
from src.models.players import Player

logger = getLogger(__name__)

class MatchDAO:
    def __init__(self, session: Session):
        # Сессия — это наше "окно" в базу данных
        self.session = session

    def get_match_by_uuid(self, uuid: str) -> Row | None:
        # Создаем "виртуальные копии" таблицы игроков
        p1 = aliased(Player)
        p2 = aliased(Player)

        match_by_uuid = (
            select(MatchModel, p1.name.label("p1_name"), p2.name.label("p2_name"))
            .join(p1, MatchModel.player_one_id == p1.id)
            .join(p2, MatchModel.player_two_id == p2.id)
            .where(MatchModel.uuid == uuid)
        )

        result = self.session.execute(match_by_uuid).first()

        return result
        # match_by_uuid = self.session.query(
        #     MatchModel,
        #     p1.name.label("p1_name"),
        #     p2.name.label("p2_name")
        # ).join(p1, MatchModel.player_one_id == p1.id) \
        #     .join(p2, MatchModel.player_two_id == p2.id) \
        #     .filter(MatchModel.uuid == uuid) \
        #     .first()

    def get_all_matches(self, page: int, page_size: int, filter_by_player_name: str = None) -> tuple[list[Row], int]:

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

        if filter_by_player_name: # and str(filter_by_player_name).strip().lower() != 'none':
            # query = query.filter(or_(p1.name.ilike(filter_by_player_name), p2.name.ilike(filter_by_player_name)))
            query = query.filter(or_(p1.name.ilike(f"%{filter_by_player_name}%"), p2.name.ilike(f"%{filter_by_player_name}%")))

        # 1. Считаем общее кол-во для пагинатора
        total_matches = query.count()
        print('total_matches', total_matches)

        # 2. Берем нужный "срез"
        offset_value = (page - 1) * page_size
        query = query.offset(offset_value).limit(page_size)

        return query.all(), total_matches  # Возвращает List[Row] и total_matches для расчета количества страниц


    def match_create(self, new_match: MatchModel) -> MatchModel:# object_model: Match) -> Match:
        self.session.add(new_match)
        # Сохраняем изменения в реальную базу данных
        self.session.commit()
        # Обновляем объект, чтобы получить его ID из базы
        self.session.refresh(new_match)
        print('new_match_dao_refresh', new_match)
        return new_match

    def select_by_uuid(self, uuid: str) -> MatchModel:
        query = select(MatchModel).where(MatchModel.uuid == uuid)
        result = self.session.execute(query).scalar_one_or_none()

        # if not result:
        #     raise MatchNotFound(uuid)

        return result



