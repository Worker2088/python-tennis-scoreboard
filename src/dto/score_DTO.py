from pydantic import BaseModel, Field, ConfigDict, computed_field
# from src.dto.match_DTO import MatchDTO
from typing import List


# class MatchScoreDisplayDTO(BaseModel):
#     set1: int = 0 # количество выигранных сетов игрока 1
#     set2: int = 0 # количество выигранных сетов игрока 2
#     game1: int = 0 # текущий счет в третьем сете
#     game2: int = 0 # текущий счет в третьем сете
#     point1: int = 0
#     point2: int = 0

class SetScoreDTO(BaseModel):
    player1_games: int = 0
    player2_games: int = 0

class MatchScoreDTO(BaseModel):
    sets: list[SetScoreDTO] = Field(default_factory=list)  # Список завершенных сетов
    current_points_p1: str = '0'  # Текущие очки в гейме (например, "15", "40" или "AD")
    current_points_p2: str = '0'
    is_tiebreak: bool = False
    current_set_index: int = 0 # индекс текущего сета

    def _count_won_sets(self) -> tuple[int, int]:
        """Вспомогательный метод: возвращает (победы_P1, победы_P2)"""
        p1_wins = 0
        p2_wins = 0
        for s in self.sets:
            # Сет считается завершенным, если кто-то выиграл больше геймов
            # При условии, что сет вообще игрался (есть геймы)
            if (s.player1_games - s.player2_games >= 2) and s.player1_games >= 6:
                p1_wins += 1
            elif (s.player2_games - s.player1_games >= 2) and s.player2_games >= 6:
                p2_wins += 1
            elif s.player1_games == 7 and s.player2_games == 6:
                p1_wins += 1
            elif s.player1_games == 6 and s.player2_games == 7:
                p2_wins += 1
        return p1_wins, p2_wins

    @computed_field
    @property
    def set1(self) -> int:
        """Общий счет по сетам для Игрока 1"""
        return self._count_won_sets()[0]

    @computed_field
    @property
    def set2(self) -> int:
        """Общий счет по сетам для Игрока 2"""
        return self._count_won_sets()[1]

    @computed_field
    @property
    def game1(self) -> int:
        # Берем последний сет из списка и смотрим геймы
        return self.sets[self.current_set_index].player1_games

    @computed_field
    @property
    def game2(self) -> int:
        return self.sets[self.current_set_index].player2_games

    @computed_field
    @property
    def point1(self) -> str:
        return self.current_points_p1

    @computed_field
    @property
    def point2(self) -> str:
        return self.current_points_p2


    model_config = ConfigDict(from_attributes=True)




