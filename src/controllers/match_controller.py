import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from pydantic import ValidationError
from src.controllers.base_controller import BaseController
from src.dto.match_DTO import MatchCreateDTO, MatchDTO
from src.services.match_service import MatchService
from src.services.score_service import ScoreService
# from src.dto.score_DTO import MatchScoreDTO, MatchScoreDisplayDTO
# from src.services.exceptions import BaseAppException, FormFieldNotFound

logger = getLogger(__name__)


class MatchController(BaseController):
    """
    Контроллер для обработки HTTP-запросов, связанных с матчами.
    """
    def __init__(self, handler: BaseHTTPRequestHandler) -> None:
        """Инициализирует контроллер и его зависимость от CurrencyService."""
        super().__init__(handler)
        self.service = MatchService()
        # self.env = Environment(loader=FileSystemLoader("templates"))

    def render_match_score(self, uuid: str) -> None:

        match_dto = self.service.get_match_by_uuid(uuid)
        print('match_dto', match_dto)

        with open(Path("templates/match-score.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        # 3. Создаем объект шаблона Jinja2
        template = Template(template_html)

        # 4. Рендерим: передаем весь match_dto целиком!
        # В HTML теперь можно обращаться к полям через {{ match.player_one_name }}
        final_html = template.render(match=match_dto)

        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(final_html.encode("utf-8"))

    def render_matches_page(self, page: int, filter_by_player_name: str = None) -> None:

        pagination_result  = self.service.get_matches_for_paginated(page, filter_by_player_name)
        print('pagination_result контроллер', pagination_result)

        with open(Path("templates/matches.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        # 3. Создаем объект шаблона Jinja2
        template = Template(template_html)

        # 4. Рендерим: передаем весь match_dto целиком!
        # В HTML теперь можно обращаться к полям через {{ match.player_one_name }}
        final_html = template.render(pagination_result=pagination_result)
        # final_html = template.render(matches=pagination_result.matches)

        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(final_html.encode("utf-8"))

    def show_main_page(self):
        template = self.env.get_template("index.html")
        rendered_page = template.render()
        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(rendered_page.encode("utf-8"))

    def show_new_match_page(self):
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
        # try:
        content_length = int(self.handler.headers.get('Content-Length', 0))
        print('content_length', content_length)
        if content_length == 0:
            print('тело POST запроса = 0')
        post_data_bytes = self.handler.rfile.read(content_length)
        print('post_data_bytes', post_data_bytes)
        post_data = urllib.parse.parse_qs(post_data_bytes.decode('utf-8'))
        print('post_data', post_data)
        normalized_data = {key: value[0] for key, value in post_data.items()}
        print('normalized_data', normalized_data)

        try:
            match_in_dto = MatchCreateDTO.model_validate(normalized_data)
            print('match_in_dto', match_in_dto)
            match_out_dto = self.service.create_match(match_in_dto)
            print('match_dto', match_out_dto)

            # 2. Формируем URL для редиректа согласно ТЗ
            # Используем f-строку для подстановки UUID
            redirect_url = f"/match-score?uuid={match_out_dto.uuid}"

            # 3. Отправляем ответ 302 (Found / Redirect) вместо 200 (OK)
            self.handler.send_response(302)
            # 4. Указываем браузеру, КУДА именно переходить
            self.handler.send_header("Location", redirect_url)
            self.handler.end_headers()
        except ValueError as e:
            # 1. Извлекаем ошибки в удобный формат: {'field_name': 'error message'}
            # errors = {err['loc'][0]: err['msg'] for err in e.errors()}
            errors = {}
            print('e.errors()', e.errors())

            for err in e.errors():
                print('err', err)
                # loc[0] - это имя поля (например, 'player_one_name')
                # field_name = err['loc'][0]
                if err['loc']:
                    field_name = err['loc'][0]
                else:
                    field_name = 'main_error'
                print('field_name', field_name)

                # Берем текст ошибки
                raw_msg = err['msg']
                print('raw_msg', raw_msg)

                # Убираем "Value error, " если оно есть в начале строки
                # В Python 3.12+ метод removeprefix — самый элегантный способ
                clean_msg = raw_msg.removeprefix("Value error, ")
                # Методы строк можно вызывать один за другим
                # clean_msg = raw_msg.removeprefix("Value error, ").removeprefix("__root__, ")

                errors[field_name] = clean_msg
                print('errors[field_name]', errors[field_name])

            # 2. Рендерим шаблон, передавая и ошибки, и введенные данные
            template = self.env.get_template("new-match.html")
            rendered_page = template.render(
                errors=errors,
                **normalized_data  # Распаковываем старые значения (player_one_name и т.д.)
            )

            # 3. Отправляем ответ
            self.handler.send_response(200)
            self.handler.send_header("Content-type", "text/html; charset=utf-8")
            self.handler.end_headers()
            self.handler.wfile.write(rendered_page.encode("utf-8"))

            # context = {
            #     "error": error_text,
            #     "player_one_name": normalized_data.get("player_one_name", ""),
            #     "player_two_name": normalized_data.get("player_two_name", "")
            # }
            #
            # self.handler.send_response(200)
            # self.handler.send_header("Content-type", "text/html")
            # self.handler.end_headers()
            # with open(Path("templates/new-match.html"), "rb") as f:
            #     self.handler.wfile.write(f.read())


            # 1. Ловим ошибку валидации.
            # В Pydantic v2 сообщение об ошибке можно достать через e.errors()
            # или просто привести к строке для кастомных ValueError.




        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # with open(Path("templates/match-score.html"), "rb") as f:
        #     self.wfile.write(f.read())
        # except BaseAppException as e:
        #     self.send_error_response(e.status_code, e.message)
        # except Exception as e:
        #     logger.error(f"Ошибка при создании валюты: {e}")
        #     self.send_error_response(500, f"Произошла внутренняя ошибка: {str(e)}")

    def change_score(self, uuid: str) -> None:
        # try:
        content_length = int(self.handler.headers.get('Content-Length', 0))
        print('change_score content_length', content_length)
        if content_length == 0:
            print('change_score тело POST запроса = 0')
        #     raise FormFieldNotFound("Тело запроса не может быть пустым")

        post_data_bytes = self.handler.rfile.read(content_length)
        print('change_score post_data_bytes', post_data_bytes)
        post_data = urllib.parse.parse_qs(post_data_bytes.decode('utf-8'))
        print('change_score post_data', post_data)
        normalized_data = {key: value[0] for key, value in post_data.items()}
        print('change_score normalized_data', normalized_data)

        # берем значение из словаря
        # name_win_point = normalized_data.values()
        name_win_point = int(next(iter(normalized_data.values())))
        print('change_score name_win_point', name_win_point)
        self.service.change_score_match_service(uuid, name_win_point)
        # print('change_score match_in_dto', match_in_dto)

        # отрисовываем страницу матча с обновленным счетом
        self.render_match_score(uuid)
        # надо изменить скор в матче с заданным uuid
        # match_in_dto = MatchCreateDTO.model_validate(normalized_data)
        # print('change_score match_in_dto', match_in_dto)

        # try:
        # match_create_dto = MatchCreateDTO.model_validate(normalized_data)
        # except ValidationError:
        #     raise FormFieldNotFound("Отсутствует или неверно заполнено одно из полей: name, code, sign")

        # match_out_dto = self.service.create_match(match_in_dto)
        # print('match_dto', match_out_dto)



        # 2. Формируем URL для редиректа согласно ТЗ
        # Используем f-строку для подстановки UUID
        # redirect_url = f"/match-score?uuid={match_out_dto.uuid}"
        #
        # # 3. Отправляем ответ 302 (Found / Redirect) вместо 200 (OK)
        # self.handler.send_response(302)
        # # 4. Указываем браузеру, КУДА именно переходить
        # self.handler.send_header("Location", redirect_url)
        # self.handler.end_headers()
    # def filter_by_name_matches(self, filter_by_player_name: str) -> None:
    #
    #     redirect_url = f"/matches?filter_by_player_name =${filter_by_player_name}"
    #     # 3. Отправляем ответ 302 (Found / Redirect) вместо 200 (OK)
    #     self.handler.send_response(302)
    #     # 4. Указываем браузеру, КУДА именно переходить
    #     self.handler.send_header("Location", redirect_url)
    #     self.handler.end_headers()



