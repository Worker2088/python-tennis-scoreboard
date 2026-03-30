"""
Модуль содержит сервис для управления логикой счета в теннисном матче.

Реализует расчет очков, геймов, сетов и тай-брейков.
"""
import logging

from src.dao.match_DAO import MatchDAO
from src.dao.player_DAO import PlayerDAO
from src.database.connection import SessionLocal
from src.dto.match_DTO import MatchCreateDTO, MatchDTO
from src.dto.score_DTO import MatchScoreDTO, SetScoreDTO
from src.models.matches import MatchModel

logger = logging.getLogger(__name__)


class ScoreService:
    """
    Сервисный слой для управления логикой счета в теннисном матче.
    """
    def __init__(self) -> None:
        """Инициализирует состояние счета матча по умолчанию."""
        self.match_score = MatchScoreDTO(
            sets=[
                SetScoreDTO(player1_games=0, player2_games=0),  # Сет 0
                SetScoreDTO(player1_games=0, player2_games=0),  # Сет 1
                SetScoreDTO(player1_games=0, player2_games=0)  # Сет 2
            ],
            current_points_p1="0",
            current_points_p2="0"
        )


    def process_point(self, match_model: MatchModel, winning_player: int) -> None:
        """
        Основной метод для обновления счета в матче.
        
        Args:
            match_model (MatchModel): Объект модели матча из БД.
            winning_player (int): Номер игрока, выигравшего очко (1 или 2).
        """

        # Умная валидация: проверяем, пришла строка или словарь
        if isinstance(match_model.score, str):
            # Если это строка (старый формат или сбой драйвера), используем парсер JSON
            score = MatchScoreDTO.model_validate_json(match_model.score)
        else:
            # Если SQLAlchemy уже вернула dict (новый формат JSON-колонки)
            score = MatchScoreDTO.model_validate(match_model.score)

        self.update_score(score, winning_player)

        # обновляю счет в объекте MatchModel
        match_model.score = score.model_dump()
        winner_number = self._check_match_winner(score)

        if winner_number:
            # Переменная создается и сразу используется
            match_model.winner_id = (
                match_model.player_one_id if winner_number == 1
                else match_model.player_two_id)



    def update_score(self, score: MatchScoreDTO, winning_player: int) -> None:
        """
        Ядро логики: обработка обычных очков и тай-брейков.
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
            winning_player (int): Номер игрока, выигравшего очко.
        """
        if score.is_tiebreak:
            self._process_tiebreak_point(score, winning_player)
        else:
            self._process_normal_point(score, winning_player)

    def _process_normal_point(self, score: MatchScoreDTO, winning_player: int) -> None:
        """
        Обработка стандартного начисления очков (0, 15, 30, 40, AD).
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
            winning_player (int): Номер игрока, выигравшего очко.
        """
        match winning_player:
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
                                self._increment_game(score, winning_player)
                    case 'AD':
                    # У первого было AD -> он выигрывает гейм
                        self._increment_game(score, winning_player)

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
                                self._increment_game(score, winning_player)
                    case 'AD':
                        # У первого было AD -> он выигрывает гейм
                        self._increment_game(score, winning_player)

    def _process_tiebreak_point(self, score: MatchScoreDTO, winning_player: int) -> None:
        """
        Обработка очков во время тай-брейка.
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
            winning_player (int): Номер игрока, выигравшего очко.
        """
        # 1. Инкрементируем простые числа (храним их как строки для консистентности)
        if winning_player == 1:
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
                score.is_tiebreak = False
                self._increment_game(score, winning_player)

            case (points1, points2) if points2 >= 7 and (points2 - points1) >= 2:
                score.is_tiebreak = False
                self._increment_game(score, winning_player)

            case _:
                # Продолжаем тай-брейк
                pass

    def _increment_game(self, score: MatchScoreDTO, winning_player: int) -> None:
        """
        Увеличивает счет геймов в текущем сете.
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
            winning_player (int): Номер игрока, выигравшего гейм.
        """
        score.current_points_p1 = '0'
        score.current_points_p2 = '0'
        current_set = score.sets[score.current_set_index]
        match winning_player:
            case 1:
                current_set.player1_games += 1
                self._check_set_winner(score)
            case 2:
                current_set.player2_games += 1
                self._check_set_winner(score)

    def _check_set_winner(self, score: MatchScoreDTO) -> None:
        """
        Проверяет, завершился ли текущий сет.
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
        """
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


    def _check_match_winner(self, score: MatchScoreDTO) -> int | None:
        """
        Проверяет, завершился ли матч.
        
        Args:
            score (MatchScoreDTO): Текущий объект счета.
            
        Returns:
            int | None: Номер победителя (1 или 2) или None, если матч продолжается.
        """
        score.current_points_p1 = '0'
        score.current_points_p2 = '0'

        # 2. Считаем, сколько сетов УЖЕ завершено
        sets_won_p1 = 0
        sets_won_p2 = 0

        for s in score.sets:
            if (s.player1_games - s.player2_games >= 2) and (s.player1_games >= 6):
                sets_won_p1 += 1
            elif (s.player2_games - s.player1_games >= 2) and (s.player2_games >= 6):
                sets_won_p2 += 1
            elif s.player1_games == 7 and s.player2_games == 6:
                sets_won_p1 += 1
            elif s.player1_games == 6 and s.player2_games == 7:
                sets_won_p2 += 1

        print('sets_won_p1', sets_won_p1)
        print('sets_won_p2', sets_won_p2)
        # 3. Проверка завершения матча (Best of 3)
        if sets_won_p1 == 2:
            print("FINISHED 1")
            return 1
        elif sets_won_p2 == 2:
            print("FINISHED 2")
            return 2
        return None

    def get_match_for_display(self, uuid: str) -> MatchDTO:
        """
        Получает данные матча для отображения на странице счета.
        
        Args:
            uuid (str): UUID матча.
            
        Returns:
            MatchDTO: DTO с данными матча и счетом.
            
        Raises:
            ValueError: Если матч не найден.
        """
        with (SessionLocal() as session):
            player_dao = PlayerDAO(session)
            match_dao = MatchDAO(session)
            match = match_dao.get_by_uuid(uuid)

            if not match:
                raise ValueError("Матч не найден!")

            player_one_model = player_dao.get_by_id(match.player_one_id)
            player_two_model = player_dao.get_by_id(match.player_two_id)
            json_score_from_db = match.score

            if isinstance(json_score_from_db, str):
                score_obj = MatchScoreDTO.model_validate_json(json_score_from_db)
            else:
                score_obj = MatchScoreDTO.model_validate(json_score_from_db)
                
            new_match_dto = MatchDTO(
                id=match.id,
                uuid=match.uuid,
                player_one_name=player_one_model.name,
                player_two_name=player_two_model.name,
                winner_id=match.winner_id,
                score=score_obj,
            )
            return new_match_dto
