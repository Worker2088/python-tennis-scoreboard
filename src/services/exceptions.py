"""
Модуль содержит кастомные исключения приложения.

Определяет базовые и специфические ошибки (например, MatchNotFound).
"""

class BaseAppException(Exception):
    """
    Базовый класс для всех кастомных исключений приложения.
    """
    def __init__(self, message: str, status_code: int = 500) -> None:
        """
        Инициализирует исключение.

        Args:
            message (str): Сообщение об ошибке.
            status_code (int): HTTP статус-код ошибки.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MatchNotFound(BaseAppException):
    """
    Исключение, выбрасываемое при отсутствии матча в базе данных.
    """
    def __init__(self, match_uuid: str) -> None:
        """
        Инициализирует ошибку поиска матча.

        Args:
            match_uuid (str): UUID матча, который не был найден.
        """
        super().__init__(f"Матч с UUID {match_uuid} не найден", status_code=404)

class DuplicatePlayerName(BaseAppException):
    """
    Исключение, выбрасываемое при попытке создать матч с одинаковыми именами игроков.
    """
    def __init__(self, message: str = "Игроки в матче должны быть разными") -> None:
        """
        Инициализирует ошибку дублирования имен.

        Args:
            message (str): Сообщение об ошибке.
        """
        super().__init__(message, status_code=400)

# class PlayerError(BaseAppException): pass
# class PlayerNotFound(PlayerError): pass
# class DuplicatePlayerName(PlayerError): pass
#
# class MatchError(BaseAppException): pass
# class MatchNotFound(MatchError): pass
# class MatchAlreadyFinished(MatchError): pass
#
# class InfrastructureError(BaseAppException): pass
# class DatabaseConnectionError(InfrastructureError): pass