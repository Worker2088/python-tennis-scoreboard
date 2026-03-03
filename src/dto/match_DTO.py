from pydantic import BaseModel, Field, ConfigDict
from typing import List
from src.dto.score_DTO import MatchScoreDTO

class MatchCreateDTO(BaseModel):
    # uuid: str
    player_one_name: str
    player_two_name: str
    # winner_id: int
    # score: str

# class MatchScoreDTO(BaseModel):
#     set1: int = 0
#     set2: int = 0
#     game1: int = 0
#     game2: int = 0
#     point1: int = 0
#     point2: int = 0
#
# class SetScore(BaseModel):
#     player1_games: int = 0
#     player2_games: int = 0
#
# class MatchScore(BaseModel):
#     sets: list[SetScore] = Field(default_factory=list)  # Список завершенных сетов
#     current_points_p1: str = '0'  # Текущие очки в гейме (например, "15", "40" или "AD")
#     current_points_p2: str = '0'

class MatchDTO(BaseModel):
    id: int
    uuid: str
    player_one_name: str
    player_two_name: str
    winner_id: int | None
    score: MatchScoreDTO = Field(default_factory=MatchScoreDTO)

    # # Как это работает в жизни:
    # score = MatchScore(
    #     sets=[SetScore(p1_games=6, p2_games=2)],  # Первый сет уже в списке
    #     current_points_p1="15"
    # )
    # # Если начался новый сет, мы просто добавляем новый "органайзер" в список:
    # score.sets.append(SetScore(p1_games=0, p2_games=1))
    # Твой пример: 2:6, 6:0, в текущем сете 0:1

    # current_match = MatchScore(
    #     sets=[
    #         SetScore(player1_games=2, player2_games=6),
    #         SetScore(player1_games=6, player2_games=0)
    #     ],
    #     current_points_p1="0",
    #     current_points_p2="15"  # Допустим, игрок 2 выиграл первый розыгрыш
    # )
    #
    # # ПРЕВРАЩАЕМ В JSON (для сохранения в БД в колонку Score)
    # json_string = current_match.model_dump_json()
    # print(f"В базу данных полетит вот такая строка: \n{json_string}")
    #
    # # ВОССТАНАВЛИВАЕМ ИЗ JSON (когда прочитали из БД)
    # restored_score = MatchScore.model_validate_json(json_string)
    # print(
    #     f"Первый сет закончился со счетом: {restored_score.sets[0].player1_games}:{restored_score.sets[0].player2_games}")



# class MatchDTO(BaseModel):
#     id: int
#     uuid: str
#     player_one_id: int
#     player_two_id: int
#     winner_id: int | None
#     score: str

    model_config = ConfigDict(from_attributes=True)



