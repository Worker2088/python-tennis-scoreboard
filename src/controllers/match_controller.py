import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from logging import getLogger
from pathlib import Path


from pydantic import ValidationError

from src.controllers.base_controller import BaseController
from src.dto.match_DTO import MatchCreateDTO, MatchDTO
from src.services.match_service import MatchService
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

    def play_match(self, uuid: str) -> None:

        match_dto = self.service.get_match_for_display(uuid)
        print('match_dto', match_dto)

        with open(Path("templates/match-score.html"), "r", encoding="utf-8") as f:
            template_html = f.read()

        match_score_dto = self.service.get_match_score_for_display(uuid)
        print('match_score_dto', match_score_dto)
        final_html = template_html.format(
            Player1 = match_dto.player_one_name,
            Player2 = match_dto.player_two_name,
            Set1 = match_score_dto.set1,
            Set2 = match_score_dto.set2,
            Game1 = match_score_dto.game1,
            Game2 = match_score_dto.game2,
            Point1 = match_score_dto.point1,
            Point2 = match_score_dto.point2,
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


    # def get_all_currencies(self) -> None:
    #     """
    #     Обрабатывает GET /currencies.
    #     Получает список всех валют и отправляет его в виде JSON-ответа.
    #     """
    #     try:
    #         all_dtos = self.service.get_all_currencies()
    #         dtos_in_dicts = [dto.model_dump() for dto in all_dtos]
    #         response_body_str = json.dumps(dtos_in_dicts, ensure_ascii=False)
    #         self.send_success_response(200, response_body_str)
    #     except Exception as e:
    #         logger.error(f"Ошибка при получении всех валют: {e}")
    #         self.send_error_response(500, f"Произошла внутренняя ошибка: {str(e)}")
    #
    # def get_currency(self, code: str) -> None:
    #     """
    #     Обрабатывает GET /currency/{code}.
    #     Получает одну валюту по коду и отправляет ее в виде JSON-ответа.
    #     В случае ошибки отправляет соответствующий HTTP-статус.
    #     Args:
    #        code (str): Трехбуквенный код валюты из URL.
    #     """
    #     try:
    #         one_dto = self.service.get_currency_by_code(code.upper())
    #         response_body_str = one_dto.model_dump_json()
    #         self.send_success_response(200, response_body_str)
    #     except BaseAppException as e:
    #         self.send_error_response(e.status_code, e.message)
    #     except Exception as e:
    #         logger.error(f"Ошибка при получении валюты {code}: {e}")
    #         self.send_error_response(500, f"Произошла внутренняя ошибка: {str(e)}")


