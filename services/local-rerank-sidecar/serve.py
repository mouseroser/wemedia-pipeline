#!/usr/bin/env python3
import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from backends import (
    OllamaBackend,
    OllamaSettings,
    RerankBackend,
    TransformersBackend,
    TransformersSettings,
)
from config import load_config


CONFIG = load_config()
logging.basicConfig(
    level=getattr(logging, CONFIG.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("local-rerank-sidecar")


def create_backend() -> RerankBackend:
    if CONFIG.backend == "transformers":
        return TransformersBackend(
            TransformersSettings(
                model_name=CONFIG.model_name,
                max_length=CONFIG.max_length,
            )
        )
    if CONFIG.backend == "ollama":
        return OllamaBackend(
            OllamaSettings(
                model_name=CONFIG.model_name,
                base_url=CONFIG.ollama_base_url,
                timeout_seconds=CONFIG.ollama_timeout_seconds,
                mode=CONFIG.ollama_mode,
                keep_alive=CONFIG.ollama_keep_alive,
            )
        )
    raise ValueError(
        f"unsupported backend: {CONFIG.backend} (expected transformers or ollama)"
    )


BACKEND = create_backend()


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalRerankSidecar/0.2"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/health", "/healthz"):
            payload = {
                "ok": True,
                "port": CONFIG.port,
                **BACKEND.health_payload(),
            }
            self._send_json(200, payload)
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/v1/rerank":
            self._send_json(404, {"error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length)

        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "invalid_json"})
            return

        query = payload.get("query")
        documents = payload.get("documents")
        top_n = payload.get("top_n")

        if not isinstance(query, str) or not isinstance(documents, list):
            self._send_json(400, {"error": "invalid_request"})
            return

        normalized_docs: list[str] = []
        for item in documents:
            if isinstance(item, str):
                normalized_docs.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                normalized_docs.append(item["text"])
            else:
                normalized_docs.append("")

        if top_n is None or not isinstance(top_n, int) or top_n <= 0:
            top_n = len(normalized_docs)

        try:
            scores = BACKEND.rerank(query, normalized_docs)
        except Exception as exc:
            logger.exception("rerank failed")
            self._send_json(500, {"error": "rerank_failed", "detail": str(exc)})
            return

        ranked = sorted(
            [
                {
                    "index": idx,
                    "relevance_score": float(score),
                }
                for idx, score in enumerate(scores)
            ],
            key=lambda item: item["relevance_score"],
            reverse=True,
        )[:top_n]

        self._send_json(
            200,
            {
                "backend": BACKEND.name,
                "model": payload.get("model") or BACKEND.model_name,
                "results": ranked,
            },
        )

    def log_message(self, fmt: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), fmt % args)


if __name__ == "__main__":
    logger.info(
        "starting local rerank sidecar on %s:%s with backend=%s model=%s",
        CONFIG.host,
        CONFIG.port,
        BACKEND.name,
        BACKEND.model_name,
    )
    server = ThreadingHTTPServer((CONFIG.host, CONFIG.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("shutting down")
        server.server_close()
        sys.exit(0)
