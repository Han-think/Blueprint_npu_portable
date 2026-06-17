#!/usr/bin/env bash
# setup_pod.sh — one-paste pod setup: deps + Ollama + model + smoke test.
# Run from the project root after uploading/unzipping into /workspace.
#   bash setup_pod.sh                 # install + pull model + 1 cubesat smoke
#   SMOKE=0 bash setup_pod.sh         # install + model only (no generation)
#   BP_LM_MODEL=qwen2.5:14b-instruct-q4_K_M bash setup_pod.sh   # different model
set -e

MODEL="${BP_LM_MODEL:-gemma2:27b-instruct-q4_K_M}"
SMOKE="${SMOKE:-1}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo "== Blueprint pod setup =="
echo "   project : $ROOT"
echo "   model   : $MODEL"

echo "== [1/4] python deps =="
pip install -q build123d numpy scipy

echo "== [2/4] install Ollama =="
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
# serve in background (idempotent)
pgrep -x ollama >/dev/null 2>&1 || (nohup ollama serve >/workspace/ollama.log 2>&1 & sleep 5)

echo "== [3/4] pull model ($MODEL) — this is the big download =="
ollama pull "$MODEL"

export BP_LM_URL="http://127.0.0.1:11434/v1"
export BP_LM_MODEL="$MODEL"
echo "== env: BP_LM_URL=$BP_LM_URL  BP_LM_MODEL=$BP_LM_MODEL =="

if [ "$SMOKE" = "1" ]; then
  echo "== [4/4] smoke: 1 cubesat candidate (this takes a while) =="
  python generate_batch.py --seeds cubesat --n 1
  echo "== corpus =="
  python 30_model/train_lora.py --inspect || true
else
  echo "== [4/4] smoke skipped (SMOKE=0). Run manually: =="
  echo "   export BP_LM_URL=$BP_LM_URL BP_LM_MODEL=$BP_LM_MODEL"
  echo "   python generate_batch.py --seeds all --per-seed 2"
fi
echo "== done. IMPORTANT: download 30_model/curation/curation_log.jsonl before stopping the pod =="
