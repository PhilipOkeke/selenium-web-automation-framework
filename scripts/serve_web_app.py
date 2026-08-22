"""Serve the static TaskFlow client and proxy same-origin API requests."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from os import getenv
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

WEB_APP_DIRECTORY = Path(__file__).resolve().parents[1] / "web_app"
API_BASE_URL = getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
WEB_HOST = getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(getenv("WEB_PORT", "3000"))


class TaskFlowHandler(SimpleHTTPRequestHandler):
    """Static file handler with a minimal reverse proxy for TaskFlow API routes."""

    def do_GET(self) -> None:  # noqa: N802
        if self._is_api_request():
            self._proxy("GET")
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        self._proxy("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self._proxy("PATCH")

    def do_DELETE(self) -> None:  # noqa: N802
        self._proxy("DELETE")

    def _is_api_request(self) -> bool:
        return self.path == "/health" or self.path.startswith("/api/")

    def _proxy(self, method: str) -> None:
        if not self._is_api_request():
            self.send_error(404, "Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length) if content_length else None
        headers = {"Accept": "application/json"}
        if self.headers.get("Content-Type"):
            headers["Content-Type"] = self.headers["Content-Type"]
        if self.headers.get("Authorization"):
            headers["Authorization"] = self.headers["Authorization"]

        request = Request(
            f"{API_BASE_URL}{self.path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=15) as response:
                self._send_proxy_response(
                    response.status,
                    response.read(),
                    response.headers.get("Content-Type", "application/json"),
                )
        except HTTPError as error:
            self._send_proxy_response(
                error.code,
                error.read(),
                error.headers.get("Content-Type", "application/json"),
            )
        except URLError as error:
            message = f'{{"detail":"TaskFlow API unavailable: {error.reason}"}}'.encode()
            self._send_proxy_response(502, message, "application/json")

    def _send_proxy_response(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)


def run_server() -> None:
    handler = partial(TaskFlowHandler, directory=str(WEB_APP_DIRECTORY))
    server = ThreadingHTTPServer((WEB_HOST, WEB_PORT), handler)
    print(f"TaskFlow web client available at http://{WEB_HOST}:{WEB_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
