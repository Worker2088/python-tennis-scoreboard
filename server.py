import http.server
import socketserver
from pathlib import Path

PORT = 8000


class TennisHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 1. Если просят главную страницу
        print(self.path)
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/index.html"), "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/new-match":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/new-match.html"), "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/matches":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(Path("templates/matches.html"), "rb") as f:
                self.wfile.write(f.read())

        # 2. Если запрос начинается на /static/
        elif self.path.startswith("/static/"):
            super().do_GET()

        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    # разрешаем повторное использование адреса
    socketserver.TCPServer.allow_reuse_address = True
    # uv run server.py
    with socketserver.TCPServer(("", PORT), TennisHandler) as httpd:
        print(f"🚀 Сервер на http://localhost:{PORT}")
        httpd.serve_forever()