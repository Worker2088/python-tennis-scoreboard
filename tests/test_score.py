"""
Модуль содержит юнит-тесты для сервиса подсчета счета.

Проверяет корректность начисления очков, геймов, сетов и тай-брейков.
"""
import pytest

from src.dto.score_DTO import MatchScoreDTO, SetScoreDTO
from src.services.score_service import ScoreService


@pytest.fixture
def score_service() -> ScoreService:
    """
    Фикстура для создания экземпляра ScoreService с начальным состоянием счета.

    Returns:
        ScoreService: Инициализированный сервис счета.
    """
    service = ScoreService()
    # Создаем базовое состояние
    service.match_score = MatchScoreDTO(
        sets=[
            SetScoreDTO(player1_games=0, player2_games=0),  # Сет 0
            SetScoreDTO(player1_games=0, player2_games=0),  # Сет 1
            SetScoreDTO(player1_games=0, player2_games=0)  # Сет 2
        ],
        current_points_p1="0",
        current_points_p2="0",
        is_tiebreak=False,
        current_set_index=0,
    )
    return service

@pytest.mark.parametrize(
    "initial_p1, initial_p2, winner, expected_p1, expected_p2",
    [
        ("0", "0", 1, "15", "0"),   # Начало матча: Игрок 1 берет очко
        ("15", "0", 1, "30", "0"),  # Игрок 1 продолжает лидировать
        ("30", "0", 1, "40", "0"),  # Игрок 1 выходит на game point
        ("40", "0", 1, "0", "0"),   # Игрок 1 выигрывает гейм (счет сбрасывается)
        ("40", "40", 1, "AD", "40"),
        ("40", "40", 2, "40", "AD"),
        ("AD", "40", 2, "40", "40"),
        ("40", "AD", 1, "40", "40"),
    ]
)
def test_point_increment(score_service: ScoreService, initial_p1: str, initial_p2: str, winner: int, expected_p1: str, expected_p2: str) -> None:
    """
    Тестирует корректность инкрементации очков в обычном гейме.
    """
    # 1. Arrange (Подготовка)
    score_service.match_score.current_points_p1 = initial_p1
    score_service.match_score.current_points_p2 = initial_p2
    
    # 2. Act (Действие)
    score_service.update_score(score_service.match_score, winner)

    # 3. Assert (Проверка)
    assert score_service.match_score.current_points_p1 == expected_p1
    assert score_service.match_score.current_points_p2 == expected_p2


@pytest.mark.parametrize(
    "initial_point_p1, initial_point_p2, initial_game_p1, initial_game_p2, winner, expected_point_p1, expected_point_p2, expected_game_p1, expected_game_p2",
    [
        ("40", "30", 0, 0, 1, "0", "0", 1, 0),
        ("30", "40", 0, 0, 2, "0", "0", 0, 1),
        ("AD", "40", 0, 0, 1, "0", "0", 1, 0),
        ("40", "AD", 0, 0, 2, "0", "0", 0, 1),
    ]
)
def test_game_increment(score_service: ScoreService, initial_point_p1: str, initial_point_p2: str, initial_game_p1: int, initial_game_p2: int, winner: int, expected_point_p1: str,
                        expected_point_p2: str, expected_game_p1: int, expected_game_p2: int) -> None:
    """
    Тестирует корректность инкрементации геймов при выигрыше очка.
    """
    # 1. Arrange (Подготовка)
    score_service.match_score.sets[0].player1_games = initial_game_p1
    score_service.match_score.sets[0].player2_games = initial_game_p2
    score_service.match_score.current_points_p1 = initial_point_p1
    score_service.match_score.current_points_p2 = initial_point_p2
    
    # 2. Act (Действие)
    score_service.update_score(score_service.match_score, winner)

    # 3. Assert (Проверка)
    assert score_service.match_score.current_points_p1 == expected_point_p1
    assert score_service.match_score.current_points_p2 == expected_point_p2
    assert score_service.match_score.sets[0].player1_games == expected_game_p1
    assert score_service.match_score.sets[0].player2_games == expected_game_p2


@pytest.mark.parametrize(
    """initial_point_p1, initial_point_p2, 
    initial_game_p1, initial_game_p2, 
    winner, 
    expected_point_p1, expected_point_p2, 
    expected_game_p1, expected_game_p2, 
    current_set_index""",
    [
        ("AD", "40", 5, 0, 1, "0", "0", 6, 0, 0),
        ("AD", "40", 5, 5, 1, "0", "0", 6, 5, 0),
        ("AD", "40", 6, 5, 1, "0", "0", 7, 5, 0),
    ]
)
def test_set_increment(
        score_service: ScoreService,
        initial_point_p1: str, initial_point_p2: str,
        initial_game_p1: int, initial_game_p2: int,
        winner: int,
        expected_point_p1: str, expected_point_p2: str,
        expected_game_p1: int,  expected_game_p2: int,
        current_set_index: int,
) -> None:
    """
    Тестирует корректность инкрементации сетов и геймов.
    """
    # 1. Arrange (Подготовка)
    current_set = score_service.match_score.current_set_index

    score_service.match_score.current_points_p1 = initial_point_p1
    score_service.match_score.current_points_p2 = initial_point_p2
    score_service.match_score.sets[current_set].player1_games = initial_game_p1
    score_service.match_score.sets[current_set].player2_games = initial_game_p2
    
    # 2. Act (Действие)
    score_service.update_score(score_service.match_score, winner)

    # 3. Assert (Проверка)
    assert score_service.match_score.current_points_p1 == expected_point_p1
    assert score_service.match_score.current_points_p2 == expected_point_p2
    assert score_service.match_score.sets[current_set].player1_games == expected_game_p1
    assert score_service.match_score.sets[current_set].player2_games == expected_game_p2


@pytest.mark.parametrize(
    "initial_point_p1, initial_point_p2, initial_game_p1, initial_game_p2, initial_is_tiebreak, winner, expected_point_p1, expected_point_p2, expected_game_p1, expected_game_p2, current_set_index, expected_is_tiebreak",
    [
        ("7", "0", 6, 6, True, 1, "0", "0", 7, 6, 0, False),
        ("0", "7", 6, 6, True, 2, "0", "0", 6, 7, 0, False),
        ("6", "6", 6, 6, True, 1, "7", "6", 6, 6, 0, True),
    ]
)
def test_tiebreak_point(
        score_service: ScoreService,
        initial_point_p1: str, initial_point_p2: str,
        initial_game_p1: int, initial_game_p2: int,
        initial_is_tiebreak: bool,
        winner: int,
        expected_point_p1: str, expected_point_p2: str,
        expected_game_p1: int,  expected_game_p2: int,
        current_set_index: int, expected_is_tiebreak: bool,
) -> None:
    """
    Тестирует корректность начисления очков в режиме тай-брейка.
    """
    # 1. Arrange (Подготовка)
    current_set = score_service.match_score.current_set_index

    score_service.match_score.current_points_p1 = initial_point_p1
    score_service.match_score.current_points_p2 = initial_point_p2
    score_service.match_score.sets[current_set].player1_games = initial_game_p1
    score_service.match_score.sets[current_set].player2_games = initial_game_p2
    score_service.match_score.is_tiebreak = initial_is_tiebreak

    # 2. Act (Действие)
    score_service.update_score(score_service.match_score, winner)

    # 3. Assert (Проверка)
    assert score_service.match_score.current_points_p1 == expected_point_p1
    assert score_service.match_score.current_points_p2 == expected_point_p2
    assert score_service.match_score.sets[current_set].player1_games == expected_game_p1
    assert score_service.match_score.sets[current_set].player2_games == expected_game_p2
    assert score_service.match_score.is_tiebreak == expected_is_tiebreak


