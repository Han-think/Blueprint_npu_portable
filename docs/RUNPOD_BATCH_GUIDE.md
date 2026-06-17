# RunPod 배치 생성 가이드

generate_batch.py를 유료 GPU 서버(RunPod 등)에서 돌릴 때의 환경 셋업,
vLLM 전환, 병렬 워커 설정을 다룬다.

---

## 1. 검증된 버전 조합 (A40 48GB 기준)

### Option A: Ollama (간단, 직렬)

| 구성 요소 | 버전 | 비고 |
|-----------|------|------|
| CUDA Driver | ≥ 12.1 | RunPod 기본 이미지 대부분 충족 |
| Ollama | latest | `curl -fsSL https://ollama.com/install.sh \| sh` |
| 모델 | qwen2.5:27b 등 | `ollama pull qwen2.5:27b` |

설치 순서:
```bash
# 1. Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 2. 백그라운드 실행
nohup ollama serve > /workspace/ollama.log 2>&1 &
sleep 5

# 3. 모델 다운로드
ollama pull qwen2.5:27b

# 4. 확인
curl http://127.0.0.1:11434/api/tags
```

**한계:** Ollama는 직렬 서버 — 동시 요청을 보내도 내부적으로 순차 처리.
BP_WORKERS 올려도 이득 없음. 빠르게 하려면 vLLM으로 전환해야 함.

---

### Option B: vLLM (배치 처리, 빠름)

vLLM은 동시 요청을 GPU 배치로 묶어 처리 → WORKERS와 함께 쓰면 2~4배 빠름.
**단, 버전 조합을 정확히 맞춰야 한다.**

#### 검증 조합 (2026-06 기준)

| 구성 요소 | 버전 | 설치 |
|-----------|------|------|
| CUDA Toolkit | **12.4** | RunPod 템플릿 선택 시 확인 |
| Python | **3.10** | `python3 --version` |
| PyTorch | **2.5.1+cu124** | 아래 순서대로 설치 |
| vLLM | **0.6.x** (0.6.6 권장) | PyTorch 먼저 설치 후 |

> CUDA 12.1 이미지에서는 vLLM 0.5.x + PyTorch 2.4.x 조합을 시도할 것.
> CUDA 11.8은 vLLM 미지원 — 피할 것.

#### 설치 순서 (반드시 이 순서대로)

```bash
# ── 0. 현재 CUDA 버전 확인 ──
nvidia-smi   # 우상단 "CUDA Version" 확인
nvcc --version  # toolkit 버전

# ── 1. 기존 PyTorch 제거 (충돌 방지) ──
pip uninstall torch torchvision torchaudio -y

# ── 2. CUDA 12.4 맞춤 PyTorch 설치 ──
pip install torch==2.5.1 torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu124

# ── 3. PyTorch-CUDA 연결 확인 (필수!) ──
python3 -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"
# True 12.4 가 나와야 함. False면 다음 단계 진행 금지.

# ── 4. vLLM 설치 ──
pip install vllm==0.6.6

# ── 5. vLLM 서버 기동 ──
nohup vllm serve Qwen/Qwen2.5-27B-Instruct \
    --host 0.0.0.0 --port 11434 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.90 \
    > /workspace/vllm.log 2>&1 &

# ── 6. 서버 준비 대기 (모델 로딩 수 분 소요) ──
sleep 60
curl http://127.0.0.1:11434/v1/models
```

#### vLLM 안 될 때 디버깅

| 증상 | 원인 / 해결 |
|------|-------------|
| `CUDA error: no kernel image` | PyTorch cu 버전과 실제 CUDA 불일치 → 1~2번 재실행 |
| `ImportError: libcudart.so` | CUDA toolkit 미설치 → RunPod 템플릿 교체 |
| `torch.cuda.is_available() = False` | PyTorch가 CPU 빌드로 설치됨 → `--index-url` 확인 |
| `OutOfMemoryError` | `--gpu-memory-utilization 0.85`로 낮추거나 `--max-model-len 4096` |
| `vllm` 설치 중 빌드 에러 | Python 3.10 확인, `pip install --upgrade pip setuptools wheel` 후 재시도 |

---

## 2. generate_batch.py 실행

### 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BP_LM_URL` | `http://127.0.0.1:1234/v1` | LLM 서버 엔드포인트 |
| `BP_LM_MODEL` | (빈 문자열 = 서버 기본) | 모델 지정 |
| `BP_WORKERS` | `1` | 서브시스템 동시 생성 워커 수 |

### Ollama로 실행 (직렬, WORKERS=1)

```bash
export BP_LM_URL=http://127.0.0.1:11434/v1
export BP_WORKERS=1

nohup python generate_batch.py --seeds all --per-seed 8 \
    >> /workspace/gen.log 2>&1 &
```

### vLLM으로 실행 (배치, WORKERS=3~4)

```bash
export BP_LM_URL=http://127.0.0.1:11434/v1
export BP_WORKERS=3    # A40 48GB + 27B 모델 기준 3~4 적정

nohup python generate_batch.py --seeds all --per-seed 8 \
    >> /workspace/gen.log 2>&1 &
```

> WORKERS 가이드: A40 48GB에서 27B 모델 → 3~4 / 7~8B 모델 → 4~6
> 너무 높이면 OOM 발생. 2부터 시작해서 올릴 것.

---

## 3. 모니터링

```bash
# 실시간 로그
tail -f /workspace/gen.log

# 진행률 (done/총개수)
cat /workspace/30_model/curation/batch_checkpoint.json

# 프로세스 생존 확인
pgrep -f generate_batch
```

---

## 4. 중단 & 이어하기

```bash
# 중단 (Ctrl+C 또는)
kill $(pgrep -f generate_batch)

# 이어하기 — checkpoint에서 재개
nohup python generate_batch.py --seeds all --per-seed 8 --resume \
    >> /workspace/gen.log 2>&1 &
```

`--resume`은 batch_checkpoint.json의 `done` 값부터 이어서 진행.
checkpoint는 candidate 1개 완료될 때마다 자동 저장됨.

---

## 5. 비용 추정 (RunPod 기준)

| 구성 | candidate당 시간 | 48개 총 시간 | A40 $0.46/hr 기준 |
|------|-----------------|-------------|-------------------|
| Ollama + WORKERS=1 | ~25분 | ~20시간 | ~$9.2 |
| vLLM + WORKERS=3 | ~7분 | ~5.5시간 | ~$2.5 |

→ vLLM 전환 시 **비용 약 3.5배 절감**.
