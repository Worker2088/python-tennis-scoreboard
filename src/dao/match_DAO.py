"""
Модуль содержит объект доступа к данным (DAO) для матчей.

Обеспечивает взаимодействие с базой данных для получения и создания матчей.
"""
from logging import getLogger

from sqlalchemy import Row, or_, select
from sqlalchemy.orm import Session, aliased

from src.models.matches import MatchModel
from src.models.players import Player

logger = getLogger(__name__)

class MatchDAO:
    """
    Класс для доступа к данным матчей в базе данных (Data Access Object).
    """
    def __init__(self, session: Session) -> None:
        """
        Инициализирует DAO сессией базы данных.

        Args:
            session (Session): Сессия SQLAlchemy.
        """
        self.session = session

    def get_match_by_uuid(self, uuid: str) -> Row | None:
        """
        Получает информацию о матче по его UUID, включая имена игроков.

        Args:
            uuid (str): UUID матча.

        Returns:
            Row | None: Строка результата с объектом матча и именами игроков или None.
        """
        # Создаем "виртуальные копии" таблицы игроков
        player_one_alias = aliased(Player)
        player_two_alias = aliased(Player)

        match_by_uuid = (
            select(MatchModel, player_one_alias.name.label("p1_name"), player_two_alias.name.label("p2_name"))
            .join(player_one_alias, MatchModel.player_one_id == player_one_alias.id)
            .join(player_two_alias, MatchModel.player_two_id == player_two_alias.id)
            .where(MatchModel.uuid == uuid)
        )

        result = self.session.execute(match_by_uuid).first()

        return result

    def get_all_matches(self, page: int, page_size: int, filter_by_player_name: str = None) -> tuple[list[Row], int]:
        """
        Получает список всех завершенных матчей с пагинацией и фильтрацией.

        Args:
            page (int): Номер текущей страницы.
            page_size (int): Количество записей на странице.
            filter_by_player_name (str, optional): Имя игрока для фильтрации.

        Returns:
            tuple[list[Row], int]: Список строк результата и общее количество подходящих матчей.
        """
        # 1. Создаем "виртуальные копии" таблицы игроков
        player_one_alias = aliased(Player)
        player_two_alias = aliased(Player)
        winner_alias = aliased(Player)

        query = self.session.query(
            MatchModel,
            player_one_alias.name.label("p1_name"),
            player_two_alias.name.label("p2_name"),
            winner_alias.name.label("winner_name")
        ).join(player_one_alias, MatchModel.player_one_id == player_one_alias.id) \
            .join(player_two_alias, MatchModel.player_two_id == player_two_alias.id) \
            .join(winner_alias, MatchModel.winner_id == winner_alias.id)

        print('Match_DAO query', query)
        print('Match_DAO query all', query.all())

        if filter_by_player_name: # and str(filter_by_player_name).strip().lower() != 'none':
            # query = query.filter(or_(p1.name.ilike(filter_by_player_name), p2.name.ilike(filter_by_player_name)))
            query = query.filter(or_(player_one_alias.name.ilike(f"%{filter_by_player_name}%"), player_two_alias.name.ilike(f"%{filter_by_player_name}%")))

        # 1. Считаем общее кол-во для пагинатора
        total_matches = query.count()
        print('total_matches', total_matches)

        # 2. Берем нужный "срез"
        offset_value = (page - 1) * page_size
        query = query.offset(offset_value).limit(page_size)

        return query.all(), total_matches  # Возвращает List[Row] и total_matches для расчета количества страниц


    def create(self, new_match: MatchModel) -> MatchModel:
        """
        Создает и сохраняет новый матч в базе данных.

        Args:
            new_match (MatchModel): Объект модели матча для сохранения.

        Returns:
            MatchModel: Сохраненный объект матча с заполненным ID.
        """
        self.session.add(new_match)
        # Сохраняем изменения в реальную базу данных
        self.session.commit()
        # Обновляем объект, чтобы получить его ID из базы
        self.session.refresh(new_match)
        print('new_match_dao_refresh', new_match)
        return new_match

    def get_by_uuid(self, uuid: str) -> MatchModel | None:
        """
        Ищет модель матча в базе данных по его UUID.

        Args:
            uuid (str): UUID матча.

        Returns:
            MatchModel | None: Объект модели матча или None.
        """
        query = select(MatchModel).where(MatchModel.uuid == uuid)
        result = self.session.execute(query).scalar_one_or_none()

        return result



