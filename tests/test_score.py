import pytest
from src.services.score_service import ScoreService
from src.dto.score_DTO import MatchScoreDTO, SetScoreDTO

class MockMatchModel:
    def __init__(self, score_dict, p1_id=1, p2_id=2):
        self.id = 100
        self.player_one_id = p1_id
        self.player_two_id = p2_id
        self.score = score_dict
        self.winner_id = None

@pytest.fixture
def service():
    return ScoreService()

@pytest.mark.parametrize("p1_in, p2_in, winner, p1_out, p2_out, is_game_won", [
    ("0", "0", 1, "15", "0"),
    ("15", "0", 1, "30", "0"),
    ("30", "0", 1, "40", "0"),
    ("40", "0", 1, "0", "0"), # выиграл 1 и обнуление поинтов
    ("40", "0", 2, "0", "15"),
    ("40", "40", 1, "AD", "40"),
    ("40", "AD", 1, "40", "40"),
    ("AD", "40", 1, "0", "0"), # выиграл 1 и обнуление поинтов
])
def test_point_logic(service, p1_in, p2_in, winner, p1_out, p2_out):
    pass


# def test_transition_to_tiebreak(service):
#     """Проверка перехода в режим тай-брейка при счете 6:6 по геймам"""
#     # Arrange: Счет 5:6, Игрок 1 выигрывает гейм
#     initial_dto = MatchScoreDTO(
#         sets=[SetScoreDTO(player1_games=5, player2_games=6)],
#         current_points_p1="40",
#         current_points_p2="0",
#         current_set_index=0,
#         is_tiebreak=False
#     )
#     match_obj = MockMatchModel(initial_dto.model_dump())
#
#     # Act
#     service.change_score_service(match_obj, number_win=1)
#
#     # Assert
#     final_score = MatchScoreDTO.model_validate(match_obj.score)
#     assert final_score.sets[0].player1_games == 6
#     assert final_score.sets[0].player2_games == 6
#     assert final_score.is_tiebreak is True

# def test_tiebreak_win_condition(service):
#     """Проверка завершения тай-брейка при счете 7:5 (по очкам в тай-брейке)"""
#     # Arrange: Счет 6:5 в тай-брейке, Игрок 1 выигрывает очко
#     initial_dto = MatchScoreDTO(
#         sets=[SetScoreDTO(player1_games=6, player2_games=6)],
#         current_points_p1="6",
#         current_points_p2="5",
#         current_set_index=0,
#         is_tiebreak=True
#     )
#     match_obj = MockMatchModel(initial_dto.model_dump())
#
#     # Act
#     service.change_score_service(match_obj, number_win=1)
#
#     # Assert
#     final_score = MatchScoreDTO.model_validate(match_obj.score)
#     assert final_score.is_tiebreak is False
#     assert final_score.sets[0].player1_games == 7
#     assert final_score.sets[0].player2_games == 6
#     # Проверяем, что индекс сета увеличился для следующего сета
#     assert final_score.current_set_index == 1
#
# def test_match_victory_best_of_three(service):
#     """Проверка определения победителя матча после выигрыша двух сетов"""
#     # Arrange: Игрок 1 уже выиграл 1 сет, и во втором сете счет 5:0, 40:0
#     initial_dto = MatchScoreDTO(
#         sets=[
#             SetScoreDTO(player1_games=6, player2_games=0), # Сет 1 за P1
#             SetScoreDTO(player1_games=5, player2_games=0), # Сет 2 в процессе
#             SetScoreDTO(player1_games=0, player2_games=0)
#         ],
#         current_points_p1="40",
#         current_points_p2="0",
#         current_set_index=1
#     )
#     # Важно: передаем ID игроков, чтобы проверить winner_id
#     match_obj = MockMatchModel(initial_dto.model_dump(), p1_id=10, p2_id=20)
#
#     # Act
#     service.change_score_service(match_obj, number_win=1)
#
#     # Assert
#     # В твоем текущем коде print("FINISHED 1"), давай проверим,
#     # записывается ли winner_id (если ты добавишь эту логику в _check_win)
#     # На данный момент в твоем коде этого нет, тест поможет это внедрить!
#     pass