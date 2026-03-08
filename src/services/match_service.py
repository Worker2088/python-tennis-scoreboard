import logging
# from typing import List

from sqlalchemy.dialects.mysql import match

from src.dao.match_DAO import MatchDAO
from src.dto.match_DTO import MatchCreateDTO, MatchDTO, MatchDisplayDTO  # , MatchScoreDTO, MatchScore
from src.dto.score_DTO import MatchScoreDTO
from src.services.score_service import ScoreService
from src.dao.player_DAO import PlayerDAO
from src.models.matches import MatchModel
# from src.services.exceptions import CurrencyAlreadyExists, CurrencyNotFound
from sqlalchemy.orm import Session, aliased
from src.database.connection import SessionLocal

logger = logging.getLogger(__name__)


class MatchService:
    """
    Сервисный слой для управления матчами
    """
    def __init__(self) -> None:
        """Инициализирует контроллер и его зависимость от CurrencyService."""
        self.service = ScoreService()

    def create_match(self, match_dto: MatchCreateDTO) -> MatchDTO:
        with (SessionLocal() as session):
            # создаю объект счета матча
            initial_score_obj = ScoreService()
            print('initial_score_obj', initial_score_obj)
            # сохраняю объект в JSON-строку для хранения в БД
            # score_json = initial_score_obj.match_score.model_dump_json()
            # ПОМЕНЯЙ !!!!!!!!!!!!!!!
            # score_json = initial_score_obj.model_dump()
            score_dict = initial_score_obj.match_score.model_dump()
            print('score_dict', score_dict)

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
            new_match_model = MatchModel(player_one_id=pl1.id, player_two_id=pl2.id, score=score_dict)
            print('new_match_model_service', new_match_model)

            new_match = match_dao.match_create(new_match_model)  # дао получает и возвращает модель
            # player_one = player_dao.select_by_id(new_match.player_one_id)
            # player_two = player_dao.select_by_id(new_match.player_two_id)
            print('new_match.score из БД', new_match.score)

            new_match_dto = MatchDTO(
                id = new_match.id,
                uuid = new_match.uuid,
                player_one_name = pl1.name,
                player_two_name = pl2.name,
                winner_id = new_match.winner_id,
                # score = new_match.score,
                score = initial_score_obj.match_score,
                )
            print('new_match_dto', new_match_dto)
            return new_match_dto

    # def convert_score_service(self, score_match:MatchScoreDTO) -> MatchScoreDisplayDTO:
    #     score = ScoreService()
    #     score_dto = score.convert_score_to_display_dto(score_match)
    #
    #     return score_dto

    def get_match_for_display(self, uuid: str) -> MatchDTO:
            with SessionLocal() as session:
                match_dao = MatchDAO(session)

                # Получаем всё сразу: (объект_матча, имя1, имя2)
                result = match_dao.get_match_with_names(uuid)
                print('result', result)

                if not result:
                    raise ValueError("Матч не найден!")

                # Распаковываем результат из кортежа
                match_obj, p1_name, p2_name = result
                print('match_obj, p1_name, p2_name', match_obj, p1_name, p2_name)

                # 1. Забираем сырые данные
                raw_score = match_obj.score

                # 2. Применяем нашу универсальную схему (Адаптер)
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
                    # Превращаем JSON-строку из БД в объект Pydantic
                    score=score_dto
                )
    def get_matches_for_display(self, filter_by_player_name: str = None) -> list[MatchDisplayDTO]:
            with SessionLocal() as session:
                match_dao = MatchDAO(session)

                # Получаем всё сразу: (список: объект_матча, имя1, имя2, имя победителя)
                rows = match_dao.get_all_matches(filter_by_player_name)
                print('rows', rows)

                if not rows:
                    # raise ValueError("Нет сыгранных матчей!")
                    return []

                list_MatchDisplayDTO = [
                    MatchDisplayDTO(
                        player_one_name=row.p1_name,
                        player_two_name=row.p2_name,
                        winner_name=row.winner_name
                    )
                    for row in rows
                ]
                print('list_MatchDisplayDTO', list_MatchDisplayDTO)
                return list_MatchDisplayDTO

    def change_score_match_service(self, uuid: str, number_win: int) -> None:
        # надо вызвать сервис который определит старый счет и добавит очко
        # далее проверит на окончание гейма, если гейм окончен то проверит сет и игру если сет окончен
        print('Сервис change_score_match_service name', number_win)
        print('Сервис change_score_match_service uuid', uuid)

        # match_dto = self.get_match_for_display(uuid)
        # print('Сервис change_score_match_service match_dto', match_dto)
        # print('Сервис change_score_match_service match_dto.score', match_dto.score)

        with SessionLocal() as session:
            match_dao = MatchDAO(session)
            match_model = match_dao.select_by_uuid(uuid)
            print('Сервис change_score_match_service match_model', match_model)
            self.service.change_score_service(match_model, number_win)
            session.commit()
            session.refresh(match_model)

        # вызываем метод скор-сервиса изменения счета передавая в него объект счет и имя
        # self.service.change_score_service(uuid, name)
        # обратно получаем объект счета с новым счетом
        # print('Сервис change_score_match_service new_score', new_score)

    # def get_match_score_for_display(self, uuid: str) -> MatchScoreDTO:
    #     with (SessionLocal() as session):
    #         player_dao = PlayerDAO(session)
    #         match_dao = MatchDAO(session)
    #         match = match_dao.select_by_uuid(uuid)
    #
    #         if not match:
    #             raise ValueError("Матч не найден!")
    #
    #         # player_one = player_dao.select_by_id(match.player_one_id)
    #         # player_two = player_dao.select_by_id(match.player_two_id)
    #         json_score_from_db = match.score
    #         score_obj = MatchScore.model_validate_json(json_score_from_db)
    #
    #         match_score_dto = MatchScoreDTO(
    #             set1=score_obj.sets[0].player1_games,
    #             set2=score_obj.sets[0].player2_games,
    #             game1=0,
    #             game2=0,
    #             point1=0,
    #             point2=0,
    #         )
    #         print('match_score_dto', match_score_dto)
    #         return match_score_dto

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

