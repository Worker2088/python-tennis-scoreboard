import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from pathlib import Path


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

    def render_match(self, uuid: str) -> None:

        match_dto = self.service.get_match_for_display(uuid)
        print('match_dto', match_dto)

        with open(Path("templates/match-score.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        # метод get_match_score_for_display должен преобразовывать
        # restored_score = MatchScoreDTO.model_validate_json(match_dto.score)
        # match_score_dto = match_dto.score
        # не понимаю как вызвать метод контроллера Скоре
        # надо в него передать модель срока и получить другую модель

        # match_score_display_dto = self.service.convert_score_service(match_dto.score)
        # print('match_score_dto', match_score_dto)
        final_html = template_html.format(
            Player1 = match_dto.player_one_name,
            Player2 = match_dto.player_two_name,
            Sets1 = match_dto.score.set1,#match_score_display_dto.set1,
            Sets2 = match_dto.score.set2,#match_score_display_dto.set2,
            Games1 = match_dto.score.game1,#match_score_display_dto.game1,
            Games2 = match_dto.score.game2,#match_score_display_dto.game2,
            Points1 = match_dto.score.point1,#match_score_display_dto.point1,
            Points2 = match_dto.score.point2,#match_score_display_dto.point2,
            match_uuid = match_dto.uuid,
            # AddScore1 = match_dto.player_one_name,
            # AddScore2 = match_dto.player_two_name,
        )

        self.handler.send_response(200)
        self.handler.send_header("Content-type", "text/html; charset=utf-8")
        self.handler.end_headers()
        self.handler.wfile.write(final_html.encode("utf-8"))


    def create_match(self) -> None:
        """
        Обрабатывает POST /new_match
        """
        # try:
        content_length = int(self.handler.headers.get('Content-Length', 0))
        print('content_length', content_length)
        if content_length == 0:
            print('тело POST запроса = 0')
        #     raise FormFieldNotFound("Тело запроса не может быть пустым")

        post_data_bytes = self.handler.rfile.read(content_length)
        print('post_data_bytes', post_data_bytes)
        post_data = urllib.parse.parse_qs(post_data_bytes.decode('utf-8'))
        print('post_data', post_data)
        normalized_data = {key: value[0] for key, value in post_data.items()}
        print('normalized_data', normalized_data)
        match_in_dto = MatchCreateDTO.model_validate(normalized_data)
        print('match_in_dto', match_in_dto)

        # try:
        # match_create_dto = MatchCreateDTO.model_validate(normalized_data)
        # except ValidationError:
        #     raise FormFieldNotFound("Отсутствует или неверно заполнено одно из полей: name, code, sign")

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
        self.render_match(uuid)
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




