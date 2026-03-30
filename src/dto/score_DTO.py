"""
Модуль содержит объекты передачи данных (DTO), связанных со счетом в матчах.

Реализует вычисляемые свойства счета сетов, геймов и очков.
"""
from pydantic import BaseModel, ConfigDict, Field, computed_field


class SetScoreDTO(BaseModel):
    """
    DTO для счета в сете.

    Attributes:
        player1_games (int): Количество геймов, выигранных первым игроком.
        player2_games (int): Количество геймов, выигранных вторым игроком.
    """
    player1_games: int = 0
    player2_games: int = 0

class MatchScoreDTO(BaseModel):
    """
    DTO для полного счета матча.

    Attributes:
        sets (list[SetScoreDTO]): Список завершенных сетов.
        current_points_p1 (str): Текущие очки первого игрока в гейме.
        current_points_p2 (str): Текущие очки второго игрока в гейме.
        is_tiebreak (bool): Флаг текущего тай-брейка.
        current_set_index (int): Индекс текущего сета.
    """
    sets: list[SetScoreDTO] = Field(default_factory=list)  # Список завершенных сетов
    current_points_p1: str = '0'  # Текущие очки в гейме (например, "15", "40" или "AD")
    current_points_p2: str = '0'
    is_tiebreak: bool = False
    current_set_index: int = 0 # индекс текущего сета

    def _count_won_sets(self) -> tuple[int, int]:
        """
        Вспомогательный метод для подсчета выигранных сетов.

        Returns:
            tuple[int, int]: Кортеж вида (победы_P1, победы_P2).
        """
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
        """
        Общий счет по сетам для Игрока 1.

        Returns:
            int: Количество выигранных сетов первого игрока.
        """
        return self._count_won_sets()[0]

    @computed_field
    @property
    def set2(self) -> int:
        """
        Общий счет по сетам для Игрока 2.

        Returns:
            int: Количество выигранных сетов второго игрока.
        """
        return self._count_won_sets()[1]

    @computed_field
    @property
    def game1(self) -> int:
        """
        Количество геймов первого игрока в текущем сете.

        Returns:
            int: Количество геймов.
        """
        # Берем последний сет из списка и смотрим геймы
        return self.sets[self.current_set_index].player1_games

    @computed_field
    @property
    def game2(self) -> int:
        """
        Количество геймов второго игрока в текущем сете.

        Returns:
            int: Количество геймов.
        """
        return self.sets[self.current_set_index].player2_games

    @computed_field
    @property
    def point1(self) -> str:
        """
        Текущие очки первого игрока в гейме.

        Returns:
            str: Очки (0, 15, 30, 40, AD).
        """
        return self.current_points_p1

    @computed_field
    @property
    def point2(self) -> str:
        """
        Текущие очки второго игрока в гейме.

        Returns:
            str: Очки (0, 15, 30, 40, AD).
        """
        return self.current_points_p2


    model_config = ConfigDict(from_attributes=True)




