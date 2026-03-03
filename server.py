import http.server
import socketserver
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
from src.controllers.match_controller import MatchController
# from src.controllers.

PORT = 8000


class TennisHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Если просят главную страницу
        print('self.path', self.path)
        # Разрезаем полный путь на составляющие
        # Если self.path был "/start?player1=Ivan&player2=Oleg"
        # То parsed_url.path станет просто "/start"
        parsed_url = urlparse(self.path)
        print('parsed_url', parsed_url)
        query = parse_qs(parsed_url.query)
        print('query', query)
        normalized_query = {key: value[0] for key, value in query.items()}
        print('normalized_query', normalized_query)

        if parsed_url.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/index.html"), "rb") as f:
                self.wfile.write(f.read())
        elif parsed_url.path == "/new-match":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/new-match.html"), "rb") as f:
                self.wfile.write(f.read())

        elif parsed_url.path == "/matches":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/matches.html"), "rb") as f:
                self.wfile.write(f.read())

        elif parsed_url.path == '/match-score':
            controller = MatchController(self)
            uuid = normalized_query.get('uuid')
            print('uuid', uuid)
            controller.render_match(uuid)

        # 2. Если запрос начинается на /static/
        elif self.path.startswith("/static/"):
            super().do_GET()

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Маршрутизирует POST-запросы."""
        print("РОУТЕР !!! ПРИШЕЛ POST ЗАПРОС !!!")
        print('ПОСТ self.path', self.path)
        parsed_url = urlparse(self.path)
        print('ПОСТ parsed_url', parsed_url)
        query = parse_qs(parsed_url.query)
        print('ПОСТ query', query)
        normalized_query = {key: value[0] for key, value in query.items()}
        print('ПОСТ normalized_query', normalized_query)

        if self.path == '/start':
            controller = MatchController(self)
            controller.create_match()

        if parsed_url.path == '/match-score':
            controller = MatchController(self)
            controller.change_score(normalized_query.get('uuid'))

if __name__ == "__main__":
    # разрешаем повторное использование адреса
    socketserver.TCPServer.allow_reuse_address = True
    # uv run server.py
    with socketserver.TCPServer(("", PORT), TennisHandler) as httpd:
        print(f"🚀 Сервер на http://localhost:{PORT}")
        httpd.serve_forever()