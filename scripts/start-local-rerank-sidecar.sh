#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/lucifinil_chen/.openclaw/workspace"
SERVICE_DIR="$ROOT/services/local-rerank-sidecar"
RUNTIME_DIR="$ROOT/runtime/local-rerank-sidecar"
LOG_FILE="$RUNTIME_DIR/server.log"
PID_FILE="$RUNTIME_DIR/server.pid"
PORT="${LOCAL_RERANK_PORT:-8765}"
HOST="${LOCAL_RERANK_HOST:-127.0.0.1}"
BACKEND="${LOCAL_RERANK_BACKEND:-transformers}"
MODEL="${LOCAL_RERANK_MODEL:-BAAI/bge-reranker-v2-m3}"
OLLAMA_BASE_URL="${LOCAL_RERANK_OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
OLLAMA_MODE="${LOCAL_RERANK_OLLAMA_MODE:-generate}"

mkdir -p "$RUNTIME_DIR"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "local-rerank-sidecar already running on $HOST:$PORT (pid $(cat "$PID_FILE"))"
  exit 0
fi

cd "$SERVICE_DIR"
uv sync >/dev/null

nohup env \
  LOCAL_RERANK_HOST="$HOST" \
  LOCAL_RERANK_PORT="$PORT" \
  LOCAL_RERANK_BACKEND="$BACKEND" \
  LOCAL_RERANK_MODEL="$MODEL" \
  LOCAL_RERANK_OLLAMA_BASE_URL="$OLLAMA_BASE_URL" \
  LOCAL_RERANK_OLLAMA_MODE="$OLLAMA_MODE" \
  uv run serve.py >>"$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"

echo "starting local-rerank-sidecar on $HOST:$PORT with backend=$BACKEND model=$MODEL"
for _ in {1..120}; do
  if curl -fsS "http://$HOST:$PORT/health" >/dev/null 2>&1; then
    echo "local-rerank-sidecar is healthy"
    exit 0
  fi
  sleep 1
done

echo "local-rerank-sidecar failed to become healthy"
exit 1
