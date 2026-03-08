# Local Rerank Sidecar

A local Jina-compatible rerank service for `memory-lancedb-pro`.

## Why this exists

- Keeps `memory-lancedb-pro` unchanged
- Exposes `POST /v1/rerank` in the format the plugin already understands
- Decouples the OpenClaw-facing API from the local inference backend
- Lets the backend evolve later without changing OpenClaw config

## Fixed external interface

- `GET /health`
- `POST /v1/rerank`

OpenClaw always talks to the same sidecar endpoint. Backends can change underneath it.

## Backends

### `transformers` (default, stable)

- Local cross-encoder via Hugging Face Transformers
- Default model: `BAAI/bge-reranker-v2-m3`
- Best current production choice on this machine

### `ollama` (optional backend)

- Keeps the same sidecar interface while moving inference behind Ollama
- Modes:
  - `generate` - use a local Ollama text model to emit JSON relevance scores
  - `embeddings` - fallback mode that ranks by Ollama embeddings cosine similarity
- This is intentionally behind the sidecar so Ollama is only one backend, not the public contract

## Key environment variables

- `LOCAL_RERANK_BACKEND=transformers|ollama`
- `LOCAL_RERANK_MODEL=...`
- `LOCAL_RERANK_OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `LOCAL_RERANK_OLLAMA_MODE=generate|embeddings`

## Scripts

- `scripts/start-local-rerank-sidecar.sh` - one-off manual start
- `scripts/stop-local-rerank-sidecar.sh` - stop one-off manual process
- `scripts/status-local-rerank-sidecar.sh` - show manual process, launchd state, and health
- `scripts/install-local-rerank-sidecar-launchd.sh` - install auto-start service via launchd
- `scripts/uninstall-local-rerank-sidecar-launchd.sh` - remove launchd service
- `scripts/switch-local-rerank-backend.sh` - switch launchd between `transformers`, `ollama-generate`, and `ollama-embeddings`

## Recommended Ollama models for Chinese-heavy memory

- `qwen2.5:7b` - recommended first model for `ollama-generate`; good Chinese ability and decent structured output
- `qwen2.5:3b` - lighter/faster trial model if you want cheaper experimentation
- `nomic-embed-text` - only for `ollama-embeddings`; useful as a fallback backend, but not a true cross-encoder reranker

## Notes

- The first `transformers` startup downloads model weights locally, so it can take a while.
- Current production default remains `transformers` for stability.
- The `ollama` backend exists so the interface is future-proof; you can experiment with it later without touching OpenClaw config.
