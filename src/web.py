"""Local web application for the Research Agent.

Run with: python -m src.web
Then open: http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import logging
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Optional
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env", encoding="utf-8-sig")

from src.agent import ResearchAgent  # noqa: E402
from src.ingest import DEFAULT_INDEX_PATH, build_index  # noqa: E402


STATIC_DIR = ROOT_DIR / "static"
TEMPLATE_DIR = ROOT_DIR / "templates"
MAX_REQUEST_BYTES = 16_384
MAX_QUESTION_CHARS = 2_000

logger = logging.getLogger(__name__)


class AgentService:
    """Lazily creates one agent after ensuring the local index exists."""

    def __init__(self) -> None:
        self._agent: Optional[ResearchAgent] = None
        self._lock = Lock()

    def ask(self, question: str) -> dict:
        with self._lock:
            if self._agent is None:
                if not Path(DEFAULT_INDEX_PATH).exists():
                    logger.info("No index found; building one from sample sources.")
                    build_index()
                self._agent = ResearchAgent()
            return self._agent.ask(question).to_dict()


service = AgentService()


class AppHandler(BaseHTTPRequestHandler):
    server_version = "ResearchAgent/1.0"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._serve_file(TEMPLATE_DIR / "index.html")
        elif path == "/health":
            self._send_json(HTTPStatus.OK, {"status": "ok"})
        elif path.startswith("/static/"):
            requested = (STATIC_DIR / path.removeprefix("/static/")).resolve()
            if STATIC_DIR.resolve() not in requested.parents:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
                return
            self._serve_file(requested)
        else:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/ask":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid request size."})
            return
        if not 0 < content_length <= MAX_REQUEST_BYTES:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request is too large."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            question = payload.get("question", "")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Enter a question to continue.")
            if len(question) > MAX_QUESTION_CHARS:
                raise ValueError(f"Questions must be under {MAX_QUESTION_CHARS} characters.")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        try:
            result = service.ask(question.strip())
            self._send_json(HTTPStatus.OK, result)
        except (RuntimeError, ValueError, FileNotFoundError) as error:
            logger.warning("Question failed: %s", error)
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": str(error)})
        except Exception:  # pragma: no cover - protects the UI from unexpected failures
            logger.exception("Unexpected question failure")
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Unexpected server error."})

    def _serve_file(self, path: Path) -> None:
        if not path.is_file():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        content = path.read_bytes()
        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        logger.info("%s - %s", self.address_string(), fmt % args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Research Agent web UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    logger.info("Research Agent UI running at http://%s:%s", args.host, args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
