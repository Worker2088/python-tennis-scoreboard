import logging
from typing import List

from src.dao.match_DAO import MatchDAO
from src.dto.match_DTO import MatchCreateDTO, MatchDTO, MatchScoreDTO
from src.dao.player_DAO import PlayerDAO
from src.models.matches import MatchModel
# from src.services.exceptions import CurrencyAlreadyExists, CurrencyNotFound
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal

logger = logging.getLogger(__name__)


class MatchService:
    """
    Сервисный слой для управления матчами
    """

    def create_match(self, match_dto: MatchCreateDTO) -> MatchDTO:
        with (SessionLocal() as session):
            player_dao = PlayerDAO(session)
            match_dao = MatchDAO(session)

            pl1 = player_dao.select_by_name(match_dto.player_one_name)
            print('pl1', pl1)
            if not pl1:
                pl1 = player_dao.add_player(match_dto.player_one_name)
                print('pl1', pl1)

            pl2 = player_dao.select_by_name(match_dto.player_two_name)
            print('pl2', pl2)
            if not pl2:
                pl2 = player_dao.add_player(match_dto.player_two_name)
                print('pl2', pl2)

            # создаем объект модели матча и передаем его в ДАО
            new_match_model = MatchModel(player_one_id=pl1.id, player_two_id=pl2.id)
            print('new_match_model_service', new_match_model)

            new_match = match_dao.match_create(new_match_model)  # дао получает и возвращает модель
            player_one = player_dao.select_by_id(new_match.player_one_id)
            player_two = player_dao.select_by_id(new_match.player_two_id)

            new_match_dto = MatchDTO(
                id = new_match.id,
                uuid = new_match.uuid,
                player_one_name = player_one.name,
                player_two_name = player_two.name,
                winner_id = new_match.winner_id,
                score = new_match.score,
                )
            print('new_match_dto', new_match_dto)
            return new_match_dto



        # with SessionLocal as session:
        #     pl1 = self.player_dao.select_by_name(match_dto.player_one_name)
        #     print('pl1', pl1)
        #     if not pl1:
        #         new_pl1 = self.player_dao.create(match_dto.player_one_name)
        #     print('new_pl1', new_pl1)
        #
        #
        # # 1. Проверяем или создаем первого игрока
        # p1 = self.player_dao.get_by_name(dto.player1_name)
        # if not p1:
        #     p1 = self.player_dao.create(dto.player1_name)
        #
        # # 2. Проверяем или создаем второго игрока
        # p2 = self.player_dao.get_by_name(dto.player2_name)
        # if not p2:
        #     p2 = self.player_dao.create(dto.player2_name)
        #
        # # 3. Создаем матч
        # new_match = self.match_dao.create(p1.id, p2.id)
        #
        # # 4. Возвращаем DTO
        # return MatchResponseDTO.from_orm(new_match)

    def get_match_for_display(self, uuid: str) -> MatchDTO:
        with (SessionLocal() as session):
            player_dao = PlayerDAO(session)
            match_dao = MatchDAO(session)
            match = match_dao.select_by_uuid(uuid)

            if not match:
                raise ValueError("Матч не найден!")

            player_one = player_dao.select_by_id(match.player_one_id)
            player_two = player_dao.select_by_id(match.player_two_id)

            new_match_dto = MatchDTO(
                id=match.id,
                uuid=match.uuid,
                player_one_name=player_one.name,
                player_two_name=player_two.name,
                winner_id=match.winner_id,
                score=match.score,
            )
            print('new_match_dto', new_match_dto)
            return new_match_dto

    def get_match_score_for_display(self, uuid: str) -> MatchScoreDTO:
        with (SessionLocal() as session):
            # player_dao = PlayerDAO(session)
            # match_dao = MatchDAO(session)
            # match = match_dao.select_by_uuid(uuid)
            # match_score = match.score

            match_score_dto = MatchScoreDTO(
                set1=0,
                set2=0,
                game1=0,
                game2=0,
                point1=0,
                point2=0,
            )
            print('match_score_dto', match_score_dto)
            return match_score_dto

    # def create_match(self, match_data: MatchCreateDTO) -> MatchDTO:
    #     """
    #     Создает новую валюту в системе.
    #     Проверяет, не существует ли уже валюта с таким кодом, перед добавлением.
    #     Args:
    #         currency_data (CurrencyCreateDTO): DTO с данными для создания новой валюты.
    #     Returns:
    #         CurrencyDTO: DTO, представляющий созданную валюту.
    #     Raises:
    #         CurrencyAlreadyExists: Если валюта с таким кодом уже существует.
    #     """
    #     code_upper = match_data.code.upper()
    #     if self.match_dao.get_by_code(code_upper):
    #         logger.warning(f"Попытка создать дубликат валюты с кодом {currency_data.code}")
    #         raise CurrencyAlreadyExists(f"Валюта с кодом '{code_upper}' уже существует")
    #     object_model = MatchCreateModel(name=currency_data.name,
    #                                        code=currency_data.code,
    #                                        sign=currency_data.sign)
    #     print('object_model', object_model)
    #     new_id = self.currency_dao.create(object_model)
    #
    #     logger.info(f"В БД добавлена новая валюта {currency_data.code}, id={new_id}")
    #
    #     return CurrencyDTO(
    #         id=new_id,
    #         code=code_upper,
    #         name=currency_data.name,
    #         sign=currency_data.sign
    #     )

    # def get_all_currencies(self) -> List[CurrencyDTO]:
    #     """
    #     Возвращает список всех валют из базы данных.
    #     Returns:
    #         List[CurrencyDTO]: Список объектов DTO валют.
    #     """
    #     all_models = self.currency_dao.get_all()
    #
    #     if all_models is None:
    #         logger.warning(f"В БД нет валют")
    #         raise CurrencyNotFound(f"В БД нет валют")
    #
    #     all_dtos = [CurrencyDTO.model_validate(model) for model in all_models]
    #
    #     logger.debug(f"Сервис получил {len(all_models)} моделей валют из DAO, преобразовал их в DTO и передал в контроллер")
    #     return all_dtos
    #
    # def get_currency_by_code(self, code: str) -> CurrencyDTO:
    #     """
    #     Находит одну валюту по ее уникальному коду.
    #     Args:
    #         code (str): Трехбуквенный код валюты (например, 'USD').
    #     Returns:
    #         CurrencyDTO: Объект DTO найденной валюты.
    #     Raises:
    #         CurrencyNotFound: Если валюта с указанным кодом не найдена в БД.
    #     """
    #     one_model = self.currency_dao.get_by_code(code)
    #
    #     if one_model is None:
    #         logger.warning(f"Валюта с кодом {code} не найдена в БД")
    #         raise CurrencyNotFound(f"Валюта с кодом {code} не найдена в БД")
    #     logger.debug(f"Сервис получил модель валюты {code} из DAO")
    #     one_dto = CurrencyDTO.model_validate(one_model)
    #
    #     return one_dto

