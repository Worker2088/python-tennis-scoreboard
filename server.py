"""
Главный модуль для запуска HTTP-сервера теннисного табло.

Настраивает обработку GET и POST запросов (маршрутизатор), инициализирует БД и запускает сервер.
"""
import http.server
import socketserver
import sys
from urllib.parse import urlparse, parse_qs

from src.controllers.match_controller import MatchController
from src.database.connection import engine
from src.models.base_model import Base

# так делаем для упрощения деплоя при помощи  Докера
# принудительно создаем БД вместо uv run alembic upgrade head
Base.metadata.create_all(bind=engine)

PORT = 8080

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class TennisHandler(http.server.SimpleHTTPRequestHandler):
    """
    Обработчик HTTP-запросов для теннисного табло
    """
    def do_GET(self) -> None:
        """
        Обрабатывает входящие GET-запросы
        """
        # 1. Если просят главную страницу
        # print('self.path', self.path)
        # Разрезаем полный путь на составляющие
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)
        normalized_query = {key: value[0] for key, value in query.items()}

        if parsed_url.path == "/":
            controller = MatchController(self)
            controller.show_main_page()

        elif parsed_url.path == "/new-match":
            controller = MatchController(self)
            controller.show_new_match_page()

        elif parsed_url.path == "/matches":
            controller = MatchController(self)
            page = normalized_query.get('page')
            filter_by_player_name = normalized_query.get('filter_by_player_name')
            print('page', page)
            print('filter_by_player_name', filter_by_player_name)
            controller.render_matches_page(page, filter_by_player_name)

        elif parsed_url.path == '/match-score':
            controller = MatchController(self)
            uuid = normalized_query.get('uuid')
            print('uuid', uuid)
            controller.render_match_score(uuid)

        # 2. Если запрос начинается на /static/
        elif self.path.startswith("/static/"):
            super().do_GET()

        else:
            self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        """
        Маршрутизирует входящие POST-запросы.
        """
        print("РОУТЕР !!! ПРИШЕЛ POST ЗАПРОС !!!")
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)
        normalized_query = {key: value[0] for key, value in query.items()}

        if self.path == '/start':
            controller = MatchController(self)
            controller.create_match()

        if parsed_url.path == '/match-score':
            controller = MatchController(self)
            controller.change_score(normalized_query.get('uuid'))

def run_server() -> None:
    """
    Запускает HTTP-сервер и настраивает обработку прерываний.
    """
    # разрешаем повторное использование адреса (при частых перезапусках)
    socketserver.TCPServer.allow_reuse_address = True
    try:
        # with socketserver.TCPServer(("0.0.0.0", PORT), TennisHandler) as httpd:
        with ThreadingTCPServer(("0.0.0.0", PORT), TennisHandler) as httpd:
            print(f"Сервер на http://localhost:{PORT}")
            print("Для остановки нажмите Ctrl+C")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        # 1. Остановка приема новых HTTP-запросов
        httpd.shutdown()

        # 2. Закрытие слушающего сокета
        httpd.server_close()
        print("Сетевой порт освобожден.")

        # 3. Очистка пула соединений БД (SQLAlchemy)
        engine.dispose()
        print("Соединения с базой данных MySQL закрыты.")

        # 4. Финальный аккорд
        print("Приложение успешно завершило работу.")
        sys.exit(0)


if __name__ == "__main__":
    run_server()