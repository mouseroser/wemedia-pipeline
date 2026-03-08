from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from .base import RerankBackend


logger = logging.getLogger("local-rerank-sidecar")


@dataclass
class OllamaSettings:
    model_name: str
    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: float = 120.0
    mode: str = "generate"
    keep_alive: str = "5m"


class OllamaBackend(RerankBackend):
    name = "ollama"

    def __init__(self, settings: OllamaSettings):
        self.model_name = settings.model_name
        self.base_url = settings.base_url.rstrip("/")
        self.timeout_seconds = settings.timeout_seconds
        self.mode = settings.mode
        self.keep_alive = settings.keep_alive
        self.client = httpx.Client(timeout=self.timeout_seconds)
        logger.info(
            "using ollama rerank backend model=%s base_url=%s mode=%s",
            self.model_name,
            self.base_url,
            self.mode,
        )

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        if self.mode == "generate":
            return self._rerank_with_generate(query, documents)
        if self.mode == "embeddings":
            return self._rerank_with_embeddings(query, documents)
        raise ValueError(
            f"unsupported ollama rerank mode: {self.mode} (expected generate or embeddings)"
        )

    def _rerank_with_generate(self, query: str, documents: list[str]) -> list[float]:
        schema = {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "integer"},
                            "score": {"type": "number"},
                        },
                        "required": ["index", "score"],
                    },
                }
            },
            "required": ["scores"],
        }
        prompt_lines = [
            "You are a reranker for search results.",
            "Given a query and candidate documents, score each document for relevance.",
            "Return ONLY JSON matching the schema.",
            "Scores must be floats between 0 and 1.",
            f"Query: {query}",
            "Documents:",
        ]
        for idx, doc in enumerate(documents):
            prompt_lines.append(f"[{idx}] {doc}")

        response = self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": "\n".join(prompt_lines),
                "stream": False,
                "format": schema,
                "keep_alive": self.keep_alive,
            },
        )
        response.raise_for_status()
        data = response.json()
        raw_response = data.get("response")
        if not isinstance(raw_response, str):
            raise ValueError("ollama generate response missing JSON body")
        parsed = json.loads(raw_response)
        scores = [0.0] * len(documents)
        for item in parsed.get("scores", []):
            if not isinstance(item, dict):
                continue
            try:
                index = int(item.get("index"))
                score = float(item.get("score"))
            except Exception:
                continue
            if 0 <= index < len(scores):
                scores[index] = _clamp_score(score)
        return scores

    def _rerank_with_embeddings(self, query: str, documents: list[str]) -> list[float]:
        query_vector = self._embed_text(query)
        return [_cosine_similarity(query_vector, self._embed_text(doc)) for doc in documents]

    def _embed_text(self, text: str) -> list[float]:
        response = self.client.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.model_name,
                "prompt": text,
                "keep_alive": self.keep_alive,
            },
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding")
        if not isinstance(embedding, list):
            raise ValueError("ollama embeddings response missing embedding vector")
        return [float(value) for value in embedding]

    def health_payload(self) -> dict[str, Any]:
        payload = super().health_payload()
        payload.update(
            {
                "baseUrl": self.base_url,
                "mode": self.mode,
            }
        )
        return payload


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("embedding vectors must have identical dimensions")
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    score = dot_product / (norm_a * norm_b)
    return _clamp_score((score + 1.0) / 2.0)
