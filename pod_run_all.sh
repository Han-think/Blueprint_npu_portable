#!/usr/bin/env bash
# pod_run_all.sh — one-shot: install proven stack + serve vLLM + parallel generate + auto-stop pod.
# Run after unzipping the repo into /workspace:
#   nohup bash pod_run_all.sh > /workspace/run_all.log 2>&1 &
#   tail -f /workspace/run_all.log
# Tunables (env): BP_LM_MODEL, PERSEED, BP_WORKERS
set -u
MODEL="${BP_LM_MODEL:-Qwen/Qwen2.5-32B-Instruct-AWQ}"
PERSEED="${PERSEED:-20}"
WORKERS="${BP_WORKERS:-8}"
export HF_HOME=/workspace/hf          # 모델을 네트워크 볼륨에 받음(영구, 재다운 방지)
cd /workspace

echo "== [1/5] system libs (build123d/OCP 의존) =="
apt-get update -qq && apt-get install -y -qq libgl1 libglu1-mesa libxrender1 libxext6 libsm6

echo "== [2/5] python deps — 검증된 조합 (vllm0.6.3 + transformers4.45.2 + build123d) =="
pip install -q build123d "vllm==0.6.3.post1" "transformers==4.45.2" || { echo "pip failed"; exit 1; }
python -c "import build123d, vllm; print('imports OK', vllm.__version__)" || { echo "import check failed"; exit 1; }

echo "== [3/5] start vLLM ($MODEL) → /workspace/hf =="
pkill -9 -f vllm 2>/dev/null || true; sleep 2
nohup python -m vllm.entrypoints.openai.api_server \
  --model "$MODEL" --port 8000 --max-model-len 8192 --gpu-memory-utilization 0.92 \
  > /workspace/vllm.log 2>&1 &

echo "== [4/5] vLLM 준비 대기 (모델 다운로드+로드, 10~20분 가능) =="
for i in $(seq 1 240); do      # 최대 ~40분
  if curl -s http://127.0.0.1:8000/v1/models 2>/dev/null | grep -q '"id"'; then
    echo "vLLM ready."; break
  fi
  if grep -qiE "no space left|out of memory|engine process failed|traceback" /workspace/vllm.log 2>/dev/null; then
    echo "!! vLLM failed — tail of /workspace/vllm.log:"; tail -25 /workspace/vllm.log; exit 1
  fi
  sleep 10
done
curl -s http://127.0.0.1:8000/v1/models | grep -q '"id"' || { echo "!! vLLM not ready in time"; tail -25 /workspace/vllm.log; exit 1; }

echo "== [5/5] 병렬 생성 (WORKERS=$WORKERS, per-seed=$PERSEED) + 끝나면 pod 자동 stop =="
rm -f 30_model/curation/batch_checkpoint.json
export BP_LM_URL=http://127.0.0.1:8000/v1
export BP_LM_MODEL="$MODEL"
export BP_WORKERS="$WORKERS"
python generate_batch.py --seeds all --per-seed "$PERSEED" >> /workspace/gen_vllm.log 2>&1
echo "=== BATCH DONE $(date) — stopping pod ===" >> /workspace/gen_vllm.log
runpodctl stop pod "$RUNPOD_POD_ID"
