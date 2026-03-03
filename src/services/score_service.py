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

    # def _update_points(self, name):
    #     pass
    # def _is_game_won(self, name):
    #     pass
    # def _is_set_won(self, name):
    #     pass
    # def _is_match_won(self, name):
    #     pass
    # def _record_game_win(self, name):
    #     pass
    # def _reset_points(self, name):
    #     pass

    def change_score_service(self, match_object: MatchModel, number_win: int) -> None:
        # надо вызвать сервис который определит старый счет и добавит очко
        # далее проверит на окончание гейма, если гейм окончен то проверит сет и игру если сет окончен
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

        if score.is_tiebreak:
            self._process_tiebreak_point(score, number_win)
        else:
            self._process_normal_point(score, number_win)

        # score_json = new_score.model_dump_json()
        # обновляю счет в объекте MatchModel
        match_object.score = score.model_dump()
        print('Сервис change_score match_object', match_object)


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

    # def _finish_tiebreak(self, score: MatchScoreDTO, number_win: int):
    #     # При победе в тай-брейке сет всегда заканчивается со счетом 7:6
    #     score.current_points_p1 = '0'
    #     score.current_points_p2 = '0'
    #     # current_set = score.sets[score.current_set_index]
    #     # if number_win == 1:
    #     #     current_set.player1_games = 7
    #     #     current_set.player2_games = 6
    #     # else:
    #     #     current_set.player1_games = 6
    #     #     current_set.player2_games = 7
    #
    #     score.is_tiebreak = False  # Выключаем режим тай-брейка
    #     # self._handle_set_end(score, number_win)

    # def _handle_set_end(self, score, number_win):
    #     pass

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
            # Случай 1: Кто-то набрал 6+, а у второго на 2 меньше
            case (g1, g2) if g1 >= 6 and (g1 - g2) >= 2:
                if score.current_set_index ==2:
                    self._check_win(score, winner=1)
                else:
                    # score.sets[score.current_set_index].player1_games = 0
                    # score.sets[score.current_set_index].player2_games = 0
                    score.current_set_index += 1
                    self._check_win(score, winner=1)

            case (g1, g2) if g2 >= 6 and (g2 - g1) >= 2:
                if score.current_set_index ==2:
                    self._check_win(score, winner=2)
                else:
                    # score.sets[score.current_set_index].player1_games = 0
                    # score.sets[score.current_set_index].player2_games = 0
                    score.current_set_index += 1
                    self._check_win(score, winner=2)

            # Случай 2: Счет 7:5 (обработка специфического случая после 6:5)
            case (7, 5):
                if score.current_set_index ==2:
                    self._check_win(score, winner=1)
                else:
                    score.current_set_index += 1
                    self._check_win(score, winner=1)
            case (5, 7):
                if score.current_set_index ==2:
                    self._check_win(score, winner=2)
                else:
                    score.current_set_index += 1
                    self._check_win(score, winner=2)

            # Случай 3: Тай-брейк (6:6)
            case (6, 6):
                score.current_points_p1 = '0'
                score.current_points_p2 = '0'
                score.is_tiebreak = True #self._start_tiebreak(score, winner_num)

            # Во всех остальных случаях сет продолжается
            case _:
                pass


    def _check_win(self, score, winner):
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
            if (s.player1_games - s.player2_games >= 2) and (s.player1_games >= 6 or s.player1_games == 7):
                sets_won_p1 += 1
                completed_sets_count += 1
                # print('sets_won_p1', sets_won_p1)

            elif (s.player2_games - s.player1_games >= 2) and (s.player2_games >= 6 or s.player2_games == 7):
                sets_won_p2 += 1
                completed_sets_count += 1
                # print('sets_won_p2', sets_won_p2)

        print('sets_won_p1', sets_won_p1)
        print('sets_won_p2', sets_won_p2)
        # 3. Проверка завершения матча (Best of 3)
        if sets_won_p1 == 2:
            print("FINISHED 1")
        elif sets_won_p2 == 2:
            print("FINISHED 2")


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
