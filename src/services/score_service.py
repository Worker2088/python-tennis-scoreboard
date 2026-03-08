import logging
from typing import List

from sqlalchemy.dialects.mysql import match

from src.dao.match_DAO import MatchDAO
from src.dto.match_DTO import MatchCreateDTO, MatchDTO
from src.dto.score_DTO import MatchScoreDTO, SetScoreDTO
from src.dao.player_DAO import PlayerDAO
from src.models.matches import MatchModel
# from src.services.exceptions import CurrencyAlreadyExists, CurrencyNotFound
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal

logger = logging.getLogger(__name__)


class ScoreService:
    """
    Сервисный слой для управления матчами
    """
    def __init__(self):
        self.match_score = MatchScoreDTO(
            sets=[
                SetScoreDTO(player1_games=0, player2_games=0),  # Сет 0
                SetScoreDTO(player1_games=0, player2_games=0),  # Сет 1
                SetScoreDTO(player1_games=0, player2_games=0)  # Сет 2
            ],
            current_points_p1="0",
            current_points_p2="0"
        )


    def change_score_service(self, match_object: MatchModel, number_win: int) -> None:
        """Входная точка: работает с моделью БД и DTO."""

        print('Сервис change_score match_object', match_object)
        print('Сервис change_score name', number_win)

        # Умная валидация: проверяем, пришла строка или словарь
        if isinstance(match_object.score, str):
            # Если это строка (старый формат или сбой драйвера), используем парсер JSON
            score = MatchScoreDTO.model_validate_json(match_object.score)
        else:
            # Если SQLAlchemy уже вернула dict (новый формат JSON-колонки)
            score = MatchScoreDTO.model_validate(match_object.score)

        print('Сервис change_score score', score)

        self.update_score(score, number_win)

        # обновляю счет в объекте MatchModel
        match_object.score = score.model_dump()
        print('Сервис change_score match_object', match_object)

        winner_number = self._check_win(score)
        print('winner_number', winner_number)

        if winner_number:
            # Переменная создается и сразу используется
            match_object.winner_id = (
                match_object.player_one_id if winner_number == 1
                else match_object.player_two_id)



    def update_score(self, score: MatchScoreDTO, number_win: int) -> None:
        """Ядро логики: здесь будет проверка на геймы, сеты и тай-брейки."""
        if score.is_tiebreak:
            self._process_tiebreak_point(score, number_win)
        else:
            self._process_normal_point(score, number_win)

    def _process_normal_point(self, score: MatchScoreDTO, number_win: int) -> None:
        match number_win:
            case 1: # если поинт выиграл первый игрок
                match score.current_points_p1:
                    case '0':
                        score.current_points_p1 = '15'
                    case '15':
                        score.current_points_p1 = '30'
                    case '30':
                        score.current_points_p1 = '40'
                    case '40':
                        match score.current_points_p2:
                            case 'AD':  # У второго было преимущество -> возвращаем в ровно
                                score.current_points_p2 = '40'
                            case '40':  # Было 40:40 -> первый получает преимущество
                                score.current_points_p1 = 'AD'
                            case _:  # У второго < 40 -> первый выиграл гейм
                                self._increment_game(score, number_win)
                    case 'AD':
                    # У первого было AD -> он выигрывает гейм
                        self._increment_game(score, number_win)

            case 2: # если поинт выиграл второй игрок
                match score.current_points_p2:
                    case '0':
                        score.current_points_p2 = '15'
                    case '15':
                        score.current_points_p2 = '30'
                    case '30':
                        score.current_points_p2 = '40'
                    case '40':
                        match score.current_points_p1:
                            case 'AD':  # У второго было преимущество -> возвращаем в ровно
                                score.current_points_p1 = '40'
                            case '40':  # Было 40:40 -> первый получает преимущество
                                score.current_points_p2 = 'AD'
                            case _:  # У второго < 40 -> первый выиграл гейм
                                self._increment_game(score, number_win)
                    case 'AD':
                        # У первого было AD -> он выигрывает гейм
                        self._increment_game(score, number_win)
        # return score

    def _process_tiebreak_point(self, score: MatchScoreDTO, number_win: int) -> None:
        # 1. Инкрементируем простые числа (храним их как строки для консистентности)
        # score.current_points_p1 = '0'
        # score.current_points_p2 = '0'
        if number_win == 1:
            current_points = int(score.current_points_p1) + 1
            score.current_points_p1 = str(current_points)
        else:
            current_points = int(score.current_points_p2) + 1
            score.current_points_p2 = str(current_points)

        # 2. Проверяем условия завершения тай-брейка через match-case
        p1 = int(score.current_points_p1)
        p2 = int(score.current_points_p2)

        match (p1, p2):
            # Кто-то набрал 7 или больше и разница >= 2
            case (points1, points2) if points1 >= 7 and (points1 - points2) >= 2:
                # self._finish_tiebreak(score, number_win)
                # score.current_points_p1 = '0'
                # score.current_points_p2 = '0'
                score.is_tiebreak = False
                self._increment_game(score, number_win)

            case (points1, points2) if points2 >= 7 and (points2 - points1) >= 2:
                # score.current_points_p1 = '0'
                # score.current_points_p2 = '0'
                score.is_tiebreak = False
                self._increment_game(score, number_win)

            case _:
                # Продолжаем тай-брейк
                pass
        # return score

    def _increment_game(self, score: MatchScoreDTO, number_win: int):
        score.current_points_p1 = '0'
        score.current_points_p2 = '0'
        current_set = score.sets[score.current_set_index]
        match number_win:
            case 1:
                current_set.player1_games += 1
                self._check_set_winner(score)
            case 2:
                current_set.player2_games += 1
                self._check_set_winner(score)

    def _check_set_winner(self, score: MatchScoreDTO):
        current_set = score.sets[score.current_set_index]
        # Создаем кортеж для сопоставления
        games = (current_set.player1_games, current_set.player2_games)

        match games:
            # Случай 1: Кто-то набрал 6+, а у второго на 2 меньше или 7:5
            case (g1, g2) if (g1 >= 6 and (g1 - g2) >= 2) or g1 == 7:
                if score.current_set_index < 2:
                    score.current_set_index += 1

            case (g1, g2) if (g2 >= 6 and (g2 - g1) >= 2) or g2 == 7:
                if score.current_set_index < 2:
                    score.current_set_index += 1

            # выиграл сет на тайбрейке со счетом 7:6
            case (g1, g2) if (g1 == 7 and g2 == 6):
                if score.current_set_index < 2:
                    score.current_set_index += 1

            case (g1, g2) if (g1 == 6 and g2 == 7):
                if score.current_set_index < 2:
                    score.current_set_index += 1

            # Случай 3: Тай-брейк (6:6)
            case (6, 6):
                score.current_points_p1 = '0'
                score.current_points_p2 = '0'
                score.is_tiebreak = True

            # Во всех остальных случаях сет продолжается
            case _:
                pass


    def _check_win(self, score) -> int | None:
        score.current_points_p1 = '0'
        score.current_points_p2 = '0'

        # 2. Считаем, сколько сетов УЖЕ завершено (где счет не 0:0 или есть победитель)
        # В теннисе сет завершен, если кто-то набрал 6+ геймов (с учетом твоей логики из _check_set_winner)
        completed_sets_count = 0
        sets_won_p1 = 0
        sets_won_p2 = 0

        for s in score.sets:
            # Проверяем, есть ли в сете победитель (логика 6+, 7:5 и т.д.)
            # Используем твою логику: если сет завершен, один из игроков выиграл его
            if (s.player1_games - s.player2_games >= 2) and (s.player1_games >= 6):
                sets_won_p1 += 1
                completed_sets_count += 1
                # print('sets_won_p1', sets_won_p1)

            elif (s.player2_games - s.player1_games >= 2) and (s.player2_games >= 6):
                sets_won_p2 += 1
                completed_sets_count += 1
                # print('sets_won_p2', sets_won_p2)
            elif s.player1_games == 7 and s.player2_games == 6:
                sets_won_p1 += 1
                completed_sets_count += 1
                # print('sets_won_p1', sets_won_p1)

            elif s.player1_games == 6 and s.player2_games == 7:
                sets_won_p2 += 1
                completed_sets_count += 1
                # print('sets_won_p2', sets_won_p2)

        print('sets_won_p1', sets_won_p1)
        print('sets_won_p2', sets_won_p2)
        # 3. Проверка завершения матча (Best of 3)
        if sets_won_p1 == 2:
            print("FINISHED 1")
            return 1
        # записать в бд победителя (по uuid)
        # обнулить поля поинт1-2 и гейм1-2
        # сделать кнопки не активными
        elif sets_won_p2 == 2:
            print("FINISHED 2")
            return 2
        return None

    def get_match_for_display(self, uuid: str) -> MatchDTO:
        with (SessionLocal() as session):
            player_dao = PlayerDAO(session)
            match_dao = MatchDAO(session)
            match = match_dao.select_by_uuid(uuid)
            print('get_match_for_display match', match)
            print('get_match_for_display match.score', match.score)

            if not match:
                raise ValueError("Матч не найден!")

            player_one = player_dao.select_by_id(match.player_one_id)
            player_two = player_dao.select_by_id(match.player_two_id)
            json_score_from_db = match.score  # '{"sets":[],"current_points_p1":"30","current_points_p2":"40"}'
            print('json_score_from_db', json_score_from_db)
            score_obj = MatchScoreDTO.model_validate_json(json_score_from_db)
            print('score_obj', score_obj)
            new_match_dto = MatchDTO(
                id=match.id,
                uuid=match.uuid,
                player_one_name=player_one.name,
                player_two_name=player_two.name,
                winner_id=match.winner_id,
                score=score_obj,
            )
            print('new_match_dto', new_match_dto)
            return new_match_dto

        # 1. Сначала просто добавляем очко игроку в текущем гейме
        # self._update_points(match_dto.score, winner_id)
        # 2. Проверяем: а не выиграл ли он гейм?
        # if self._is_game_won(match_dto.score):
        #     self._record_game_win(match_dto.score, winner_id)
        #     self._reset_points(match_dto.score)  # Очки сбрасываются в 0
        #
        #     # 3. Раз выигран гейм, проверяем: а не выигран ли сет?
        #     if self._is_set_won(match_dto.score):
        #         self._record_set_win(match_dto.score)
        #
        #         # 4. Раз выигран сет, проверяем: а не выигран ли матч?
        #         if self._is_match_won(match_dto.score):
        #             match_dto.winner_id = winner_id  # Ура, у нас есть чемпион!
        #
        # return match_dto

    # def convert_score_to_display_dto(self, match: MatchScoreDTO) -> MatchScoreDisplayDTO:
    #     # 1. Определяем выигранные сеты
    #     # Все сеты, кроме последнего — это завершенные сеты
    #     completed_sets = match.sets[:-1]
    #
    #     s1_count = 0
    #     s2_count = 0
    #
    #     for s in completed_sets:
    #         if s.player1_games > s.player2_games:
    #             s1_count += 1
    #             print('s1_count', s1_count)
    #         elif s.player1_games < s.player2_games:
    #             s2_count += 1
    #             print('s2_count', s2_count)
    #
    #     print('s1_count', s1_count)
    #     print('s2_count', s2_count)
    #
    #     # 2. Получаем текущие геймы (из последнего сета в списке)
    #     # В теннисе последний сет в списке — это тот, который идет сейчас
    #     current_set = match.sets[-1]
    #
    #     # 3. Собираем DTO
    #     return MatchScoreDisplayDTO(
    #         set1=s1_count,
    #         set2=s2_count,
    #         game1=current_set.player1_games,
    #         game2=current_set.player2_games,
    #         point1=match.current_points_p1,
    #         point2=match.current_points_p2
    #     )
