#!/bin/bash
# setup_runpod.sh — RunPod A40 원샷 셋업 (vLLM 황금조합)
# Usage: cd /workspace/Blueprint_ipex_portable && bash setup_runpod.sh
set -e

echo "=== [1/5] 의존성 황금조합 설치 ==="
pip install torch==2.4.0 vllm==0.5.5 transformers==4.44.2 outlines==0.0.46

echo "=== [2/5] pyairports stub 생성 ==="
# pip 버전(0.0.1)에는 airports.py가 없어서 vLLM import 실패
# 항상 덮어쓰기로 확실하게 처리
SITE=$(python -c "import site; print(site.getsitepackages()[0])")
mkdir -p "$SITE/pyairports"
cat > "$SITE/pyairports/__init__.py" << 'PYEOF'
airport_list = []
AIRPORT_LIST = []
PYEOF
cat > "$SITE/pyairports/airports.py" << 'PYEOF'
AIRPORT_LIST = []
PYEOF
python -c "from pyairports.airports import AIRPORT_LIST; print('pyairports stub OK')"

echo "=== [3/5] pip 캐시 정리 ==="
pip cache purge 2>/dev/null || true
rm -rf /root/.cache/pip/

echo "=== [4/5] vLLM 서버 기동 ==="
export HF_HOME=${HF_HOME:-/workspace/hf_cache}
nohup python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 24576 \
    --gpu-memory-utilization 0.92 \
    > /workspace/vllm.log 2>&1 &

echo "=== [5/5] 서버 대기 (Ctrl+C로 로그 보기 중단 가능) ==="
echo "모델 다운로드 포함 시 5-10분 소요"
tail -f /workspace/vllm.log &
TAIL_PID=$!

# "Application startup complete" 대기
while ! grep -q "Application startup complete" /workspace/vllm.log 2>/dev/null; do
    sleep 5
done
kill $TAIL_PID 2>/dev/null || true

echo "=== [CLEANUP] HF blobs 정리 (모델은 이미 VRAM에 로드됨) ==="
rm -rf /root/.cache/huggingface/hub/models--*/blobs/ 2>/dev/null || true
echo "디스크 여유: $(df -h / | tail -1 | awk '{print $4}')"

echo ""
echo "============================================"
echo "  vLLM 서버 준비 완료!"
echo "  배치 실행:"
echo "    BP_LM_URL=http://127.0.0.1:8000/v1 \\"
echo "    BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \\"
echo "    BP_WORKERS=12 \\"
echo "    BP_SKIP_AUDIT=1 \\"
echo "    python generate_batch.py --seeds all --per-seed 30"
echo "============================================"
