"""
Модуль содержит сервис для управления бизнес-логикой матчей.

Реализует операции создания матча, получения его данных и пагинации списка.
"""
import logging
import math

from src.dao.match_DAO import MatchDAO
from src.dao.player_DAO import PlayerDAO
from src.database.connection import SessionLocal
from src.dto.match_DTO import MatchCreateDTO, MatchDTO, MatchDisplayDTO, PaginatedMatches
from src.dto.score_DTO import MatchScoreDTO
from src.models.matches import MatchModel
from src.services.score_service import ScoreService

logger = logging.getLogger(__name__)


class MatchService:
    """
    Сервисный слой для управления матчами.
    """
    def __init__(self) -> None:
        """Инициализирует сервис и его зависимость от ScoreService."""
        self.service = ScoreService()

    def create_match(self, match_dto: MatchCreateDTO) -> MatchDTO:
        """
        Создает новый матч, игроков (если они не существуют) и инициализирует счет.

        Args:
            match_dto (MatchCreateDTO): Данные для создания матча (имена игроков).

        Returns:
            MatchDTO: Данные созданного матча.
        """
        with (SessionLocal() as session):
            initial_score_obj = ScoreService()
            # сохраняю объект в JSON-строку для хранения в БД
            score_dict = initial_score_obj.match_score.model_dump()

            player_dao = PlayerDAO(session)
            match_dao = MatchDAO(session)

            player_one = player_dao.get_by_name(match_dto.player_one_name)
            if not player_one:
                player_one = player_dao.create(match_dto.player_one_name)

            player_two = player_dao.get_by_name(match_dto.player_two_name)
            if not player_two:
                player_two = player_dao.create(match_dto.player_two_name)

            # создаем объект модели матча и передаем его в ДАО
            new_match_model = MatchModel(player_one_id=player_one.id, player_two_id=player_two.id, score=score_dict)

            new_match = match_dao.create(new_match_model)  # дао получает и возвращает модель

            new_match_dto = MatchDTO(
                id = new_match.id,
                uuid = new_match.uuid,
                player_one_name = player_one.name,
                player_two_name = player_two.name,
                winner_id = new_match.winner_id,
                # score = new_match.score,
                score = initial_score_obj.match_score,
                )
            return new_match_dto

    def get_match_by_uuid(self, uuid: str) -> MatchDTO:
            """
            Получает полную информацию о матче по его UUID.

            Args:
                uuid (str): UUID матча.

            Returns:
                MatchDTO: DTO с данными матча и счетом.
            """
            with SessionLocal() as session:
                match_dao = MatchDAO(session)

                # Получаем всё сразу: (объект_матча, имя1, имя2)
                result = match_dao.get_match_by_uuid(uuid)

                # Распаковываем результат из кортежа
                match_obj, p1_name, p2_name = result

                # 1. Забираем сырые данные
                raw_score = match_obj.score

                # 2. Применяем универсальную схему
                if isinstance(raw_score, str):
                    # Для старых строковых записей
                    score_dto = MatchScoreDTO.model_validate_json(raw_score)
                else:
                    # Для новых записей в формате JSON/dict
                    score_dto = MatchScoreDTO.model_validate(raw_score)

                # Создаем итоговый DTO
                return MatchDTO(
                    id=match_obj.id,
                    uuid=match_obj.uuid,
                    player_one_name=p1_name,
                    player_two_name=p2_name,
                    winner_id=match_obj.winner_id,
                    score=score_dto
                )

    def get_paginated_matches(self, page: int, filter_by_player_name: str = None) -> PaginatedMatches:
        """
        Получает список завершенных матчей с поддержкой пагинации и фильтрации.

        Args:
            page (int): Номер текущей страницы.
            filter_by_player_name (str, optional): Имя игрока для фильтрации.

        Returns:
            PaginatedMatches: Объект с результатами пагинации.
        """
        if page is None:
            page = 1
        else:
            page = int(page)
        if page < 1:
            page = 1

        page_size = 2

        with SessionLocal() as session:
            match_dao = MatchDAO(session)

            # Получаем tuple[list[Row], int] где int это общее количество матчей
            result = match_dao.get_all_matches(page, page_size, filter_by_player_name)
            rows, total_count = result

            if not rows:
                return PaginatedMatches(
                matches=[],
                filter_by_player_name=filter_by_player_name,
                total_pages=1,  # Минимум 1 страница, даже если матчей 0
                current_page=1,
                has_prev=False,
                has_next=False
            )

            dtos = [
                MatchDisplayDTO(
                    player_one_name=row.p1_name,
                    player_two_name=row.p2_name,
                    winner_name=row.winner_name
                )
                for row in rows
            ]
            if total_count == 0:
                total_pages = 1
            else:
                total_pages = math.ceil(total_count / page_size)

            return PaginatedMatches(
                matches=dtos,
                filter_by_player_name=filter_by_player_name,
                total_pages=max(1, total_pages),  # Минимум 1 страница, даже если матчей 0
                current_page=page,
                has_prev=page > 1,
                has_next=page < total_pages
            )

    def update_match_score(self, uuid: str, winning_player: int) -> None:
        """
        Обновляет счет матча на основе того, какой игрок выиграл очко.

        Args:
            uuid (str): UUID матча.
            winning_player (int): Номер игрока, выигравшего очко (1 или 2).
        """
        # надо вызвать сервис который определит старый счет и добавит очко
        # далее проверит на окончание гейма, если гейм окончен то проверит сет и игру если сет окончен
        print('Сервис update_match_score name', winning_player)
        print('Сервис update_match_score uuid', uuid)

        with SessionLocal() as session:
            match_dao = MatchDAO(session)
            match_model = match_dao.get_by_uuid(uuid)
            self.service.process_point(match_model, winning_player)
            session.commit()
            session.refresh(match_model)



