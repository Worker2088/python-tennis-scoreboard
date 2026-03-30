"""
Модуль содержит базовый контроллер для обработки HTTP-запросов.

Предоставляет общую логику для отправки успешных ответов и сообщений об ошибках.
"""
import json
from http.server import BaseHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader


class BaseController:
    """
    Базовый контроллер, предоставляющий общие методы для работы с HTTP-запросами.
    """
    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Инициализирует базовый контроллер.

        Args:
            handler (BaseHTTPRequestHandler): Обработчик HTTP-запросов.
        """
        self.handler = handler
        self.env = Environment(loader=FileSystemLoader("templates"))

    def send_success_response(self, status_code: int = 200, body: str | None = None) -> None:
        """
        Отправляет успешный HTTP-ответ.

        Args:
            status_code (int): HTTP статус-код (по умолчанию 200).
            body (str, optional): Тело ответа в формате строки.
        """
        self.handler.send_response(status_code)
        self.handler.send_header('Content-type', 'application/json; charset=utf-8')
        self.handler.end_headers()
        if body:
            # Если тело ответа есть, кодируем его и отправляем
            self.handler.wfile.write(body.encode('utf-8'))

    def send_error_response(self, status_code: int, message: str) -> None:
        """
        Отправляет JSON-ответ с сообщением об ошибке.

        Args:
            status_code (int): HTTP статус-код ошибки.
            message (str): Текст сообщения об ошибке.
        """
        self.handler.send_response(status_code)
        self.handler.send_header('Content-type', 'application/json; charset=utf-8')
        self.handler.end_headers()

        response = {
            "error": {
                "message": message
            }
        }
        self.handler.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

