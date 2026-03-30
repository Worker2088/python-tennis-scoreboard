import json
from http.server import BaseHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader


class BaseController:
    """
    Базовый контроллер, предоставляющий общие методы для отправки HTTP-ответов.
    """
    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Инициализирует контроллер.
        Args:
            handler (BaseHTTPRequestHandler): Экземпляр обработчика запроса,
                через который можно отправлять ответы.
        """
        self.handler = handler
        self.env = Environment(loader=FileSystemLoader("templates"))

    def send_success_response(self, status_code=200, body=None) -> None:
        """
        Отправляет успешный HTTP-ответ с указанным статусом и телом.
        Args:
            status_code (int): HTTP-статус ответа (например, 200, 201).
            body (str): Тело ответа, обычно в формате JSON.
        """
        self.handler.send_response(status_code)
        self.handler.send_header('Content-type', 'application/json; charset=utf-8')
        self.handler.end_headers()
        if body:
            # Если тело ответа есть, кодируем его и отправляем
            self.handler.wfile.write(body.encode('utf-8'))

    def send_error_response(self, status_code: int, message: str) -> None:
        """
        Отправляет форматированный JSON-ответ об ошибке.
        Args:
            status_code (int): HTTP-статус ошибки (например, 400, 404, 500).
            message (str): описание ошибки.
        """
        self.handler.send_response(status_code)
        self.handler.send_header('Content-type', 'application/json; charset=utf-8')
        self.handler.end_headers()
        
        response = {
            "error": {
                "message": message
            }
        }
        # json.dumps с ensure_ascii=False для корректной обработки кириллицы
        self.handler.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

