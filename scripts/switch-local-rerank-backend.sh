#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/lucifinil_chen/.openclaw/workspace"
PLIST_SRC="$ROOT/services/local-rerank-sidecar/com.openclaw.local-rerank-sidecar.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.openclaw.local-rerank-sidecar.plist"
INSTALL_SCRIPT="$ROOT/scripts/install-local-rerank-sidecar-launchd.sh"
STATUS_SCRIPT="$ROOT/scripts/status-local-rerank-sidecar.sh"

PRESET="${1:-}"
CUSTOM_MODEL="${2:-}"

if [[ -z "$PRESET" ]]; then
  cat <<'EOF'
Usage:
  switch-local-rerank-backend.sh transformers [model]
  switch-local-rerank-backend.sh ollama-generate [model]
  switch-local-rerank-backend.sh ollama-embeddings [model]

Examples:
  switch-local-rerank-backend.sh transformers
  switch-local-rerank-backend.sh ollama-generate qwen2.5:7b
  switch-local-rerank-backend.sh ollama-embeddings nomic-embed-text
EOF
  exit 1
fi

case "$PRESET" in
  transformers)
    BACKEND="transformers"
    MODE="generate"
    MODEL="${CUSTOM_MODEL:-BAAI/bge-reranker-v2-m3}"
    ;;
  ollama-generate)
    BACKEND="ollama"
    MODE="generate"
    MODEL="${CUSTOM_MODEL:-qwen2.5:7b}"
    ;;
  ollama-embeddings)
    BACKEND="ollama"
    MODE="embeddings"
    MODEL="${CUSTOM_MODEL:-nomic-embed-text}"
    ;;
  *)
    echo "Unknown preset: $PRESET" >&2
    exit 1
    ;;
esac

export PLIST_SRC PLIST_DST BACKEND MODE MODEL
python3 - <<'PY'
import os
import plistlib
from pathlib import Path

for key in ("PLIST_SRC", "PLIST_DST"):
    path = Path(os.environ[key])
    if not path.exists():
        raise SystemExit(f"Missing plist: {path}")

for plist_path in (Path(os.environ["PLIST_SRC"]), Path(os.environ["PLIST_DST"])):
    with plist_path.open("rb") as f:
        data = plistlib.load(f)
    env = data.setdefault("EnvironmentVariables", {})
    env["LOCAL_RERANK_BACKEND"] = os.environ["BACKEND"]
    env["LOCAL_RERANK_MODEL"] = os.environ["MODEL"]
    env["LOCAL_RERANK_OLLAMA_MODE"] = os.environ["MODE"]
    with plist_path.open("wb") as f:
        plistlib.dump(data, f)
PY

"$INSTALL_SCRIPT"

for _ in {1..120}; do
  if "$STATUS_SCRIPT" >/dev/null 2>&1; then
    "$STATUS_SCRIPT"
    echo "switched local-rerank-sidecar to backend=$BACKEND mode=$MODE model=$MODEL"
    exit 0
  fi
  sleep 1
done

"$STATUS_SCRIPT"
exit 1
