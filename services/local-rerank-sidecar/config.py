from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class SidecarConfig:
    host: str = "127.0.0.1"
    port: int = 8765
    backend: str = "transformers"
    model_name: str = "BAAI/bge-reranker-v2-m3"
    max_length: int = 512
    log_level: str = "INFO"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_mode: str = "generate"
    ollama_timeout_seconds: float = 120.0
    ollama_keep_alive: str = "5m"


def load_config() -> SidecarConfig:
    return SidecarConfig(
        host=os.environ.get("LOCAL_RERANK_HOST", "127.0.0.1"),
        port=int(os.environ.get("LOCAL_RERANK_PORT", "8765")),
        backend=os.environ.get("LOCAL_RERANK_BACKEND", "transformers"),
        model_name=os.environ.get(
            "LOCAL_RERANK_MODEL", "BAAI/bge-reranker-v2-m3"
        ),
        max_length=int(os.environ.get("LOCAL_RERANK_MAX_LENGTH", "512")),
        log_level=os.environ.get("LOCAL_RERANK_LOG_LEVEL", "INFO").upper(),
        ollama_base_url=os.environ.get(
            "LOCAL_RERANK_OLLAMA_BASE_URL", "http://127.0.0.1:11434"
        ),
        ollama_mode=os.environ.get("LOCAL_RERANK_OLLAMA_MODE", "generate"),
        ollama_timeout_seconds=float(
            os.environ.get("LOCAL_RERANK_OLLAMA_TIMEOUT_SECONDS", "120")
        ),
        ollama_keep_alive=os.environ.get("LOCAL_RERANK_OLLAMA_KEEP_ALIVE", "5m"),
    )
