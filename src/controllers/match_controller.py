"""
Модуль содержит контроллер для обработки запросов, связанных с теннисными матчами.

Обрабатывает рендеринг страниц счета, списка матчей и создание новых матчей.
"""
import urllib.parse
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from pathlib import Path

from jinja2 import Template

from src.controllers.base_controller import BaseController
from src.dto.match_DTO import MatchCreateDTO
from src.services.match_service import MatchService

logger = getLogger(__name__)


class MatchController(BaseController):
    """
    Контроллер для обработки HTTP-запросов, связанных с теннисными матчами.
    """
    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """
        Инициализирует контроллер матчей.

        Args:
            handler (BaseHTTPRequestHandler): Обработчик HTTP-запросов.
        """
        super().__init__(handler)
        self.service = MatchService()

    def render_match_score(self, uuid: str) -> None:
        """
        Рендерит страницу со счетом конкретного матча.

        Args:
            uuid (str): Уникальный идентификатор матча.
        """
        match_dto = self.service.get_match_by_uuid(uuid)

        with open(Path("templates/match-score.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        # Создаем объект шаблона Jinja2
        template = Template(template_html)

        # Рендерим: передаем весь match_dto целиком!
        # В HTML теперь можно обращаться к полям через {{ match.player_one_name }}
        final_html = template.render(match=match_dto)

        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(final_html.encode("utf-8"))

    def render_matches_page(self, page: int, filter_by_player_name: str = None) -> None:
        """
        Рендерит страницу со списком завершенных матчей.

        Args:
            page (int): Номер текущей страницы.
            filter_by_player_name (str, optional): Имя игрока для фильтрации списка.
        """
        pagination_result  = self.service.get_paginated_matches(page, filter_by_player_name)

        with open(Path("templates/matches.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        # Создаем объект шаблона Jinja2
        template = Template(template_html)

        # Рендерим: передаем весь match_dto целиком!
        final_html = template.render(pagination_result=pagination_result)

        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(final_html.encode("utf-8"))

    def show_main_page(self) -> None:
        """
        Отображает главную страницу приложения.
        """
        template = self.env.get_template("index.html")
        rendered_page = template.render()
        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(rendered_page.encode("utf-8"))

    def show_new_match_page(self) -> None:
        """
        Отображает страницу создания нового матча.
        """
        # 1. Получаем шаблон из нашего окружения (которое мы сохранили в self.env)
        template = self.env.get_template("new-match.html")

        # 2. Рендерим его БЕЗ данных (или с пустыми значениями)
        # Даже если данных нет, метод render превратит {{ ... }} в пустые строки
        rendered_page = template.render(errors={}, player_one_name="", player_two_name="")

        # 3. Отправляем результат
        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(rendered_page.encode("utf-8"))

    def create_match(self) -> None:
        """
        Обрабатывает POST /new_match
        """
        content_length = int(self.handler.headers.get('Content-Length', 0))
        if content_length == 0:
            print('тело POST запроса = 0')
        post_data_bytes = self.handler.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data_bytes.decode('utf-8'))
        normalized_data = {key: value[0] for key, value in post_data.items()}

        try:
            match_in_dto = MatchCreateDTO.model_validate(normalized_data)
            match_out_dto = self.service.create_match(match_in_dto)

            # Формируем URL для редиректа согласно ТЗ
            # Используем f-строку для подстановки UUID
            redirect_url = f"/match-score?uuid={match_out_dto.uuid}"

            # Отправляем ответ 302 (Found / Redirect) вместо 200 (OK)
            self.handler.send_response(302)
            # Указываем браузеру, КУДА именно переходить
            self.handler.send_header("Location", redirect_url)
            self.handler.end_headers()
        except ValueError as e:
            # Извлекаем ошибки в удобный формат: {'field_name': 'error message'}
            # errors = {err['loc'][0]: err['msg'] for err in e.errors()}
            errors = {}
            print('e.errors()', e.errors())

            for err in e.errors():
                print('err', err)
                if err['loc']:
                    field_name = err['loc'][0]
                else:
                    field_name = 'main_error'

                # Берем текст ошибки
                raw_msg = err['msg']

                # Убираем "Value error, " если оно есть в начале строки
                # В Python 3.12+ метод removeprefix для этого
                clean_msg = raw_msg.removeprefix("Value error, ")
                # Методы строк можно вызывать один за другим
                # clean_msg = raw_msg.removeprefix("Value error, ").removeprefix("__root__, ")

                errors[field_name] = clean_msg

            # Рендерим шаблон, передавая и ошибки, и введенные данные
            template = self.env.get_template("new-match.html")
            rendered_page = template.render(
                errors=errors,
                **normalized_data  # Распаковываем старые значения (player_one_name и т.д.)
            )

            # Отправляем ответ
            self.handler.send_response(200)
            self.handler.send_header("Content-type", "text/html; charset=utf-8")
            self.handler.end_headers()
            self.handler.wfile.write(rendered_page.encode("utf-8"))


    def change_score(self, uuid: str) -> None:
        """
        Обрабатывает POST-запрос на изменение счета в матче.

        Args:
            uuid (str): UUID матча.
        """
        content_length = int(self.handler.headers.get('Content-Length', 0))
        # if content_length == 0:
        #     print('change_score тело POST запроса = 0')

        post_data_bytes = self.handler.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data_bytes.decode('utf-8'))
        normalized_data = {key: value[0] for key, value in post_data.items()}

        # берем значение из словаря (номер игрока, который выиграл очко)
        winning_player = int(next(iter(normalized_data.values())))
        self.service.update_match_score(uuid, winning_player)

        # отрисовываем страницу матча с обновленным счетом
        self.render_match_score(uuid)




