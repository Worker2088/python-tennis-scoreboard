
class BaseAppException(Exception):
    """
    Базовый класс для всех кастомных исключений нашего приложения.
    Позволяет ловить все наши ошибки одним 'except BaseAppException:'.
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class MatchNotFound(BaseAppException):
    """Выбрасывается, если запрашиваемый UUID матча отсутствует в БД или памяти."""
    def __init__(self, match_uuid: str):
        super().__init__(f"Матч с UUID {match_uuid} не найден", status_code=404)

class DuplicatePlayerName(BaseAppException):
    """Выбрасывается при попытке создать матч с одинаковыми игроками."""
    def __init__(self, message: str = "Игроки в матче должны быть разными"):
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