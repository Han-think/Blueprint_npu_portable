# RunPod 배치 생성 가이드

generate_batch.py를 유료 GPU 서버(RunPod 등)에서 돌릴 때의 환경 셋업,
vLLM 전환, 병렬 워커 설정, LoRA 학습까지 다룬다.

---

## 0. 원샷 복붙 스크립트 (vLLM, 검증 완료)

> Pod 생성 후 터미널 열고 아래를 **순서대로 복붙**하면 끝.
> 템플릿: **RunPod PyTorch 2.4.0** / GPU: **A40 48GB** / 디스크: 50GB+

```bash
# ── Step 1: 코드 클론 ──
cd /workspace
git clone https://github.com/Han-think/Blueprint_npu_portable.git
cd Blueprint_npu_portable

# ── Step 2: vLLM 서버 기동 ──
# ⚠️ --max-model-len 16384 필수! (8192면 400 에러 남)
nohup vllm serve Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 16384 \
    --gpu-memory-utilization 0.90 \
    > /workspace/vllm.log 2>&1 &

# ── Step 3: 서버 올라올 때까지 대기 ──
tail -f /workspace/vllm.log
# "Application startup complete" 뜨면 Ctrl+C
```

```bash
# ── Step 4: 배치 생성 시작 ──
cd /workspace/Blueprint_npu_portable
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_WORKERS=12 \
BP_SKIP_AUDIT=1 \
nohup python generate_batch.py --seeds all --per-seed 50 \
    >> /workspace/gen.log 2>&1 &

# ── Step 5: 30초 후 로그 확인 ──
sleep 30 && tail -20 /workspace/gen.log
```

```bash
# ── Step 6: 완료 후 Git push ──
cd /workspace/Blueprint_npu_portable
git add 30_model/curation/
git commit -m "batch: 300 candidates via vLLM Qwen2.5-14B"
git push
```

---

## 1. 검증된 버전 조합 (A40 48GB 기준)

### Option A: Ollama (간단, 직렬) — 비추천

| 구성 요소 | 버전 | 비고 |
|-----------|------|------|
| CUDA Driver | ≥ 12.1 | RunPod 기본 이미지 대부분 충족 |
| Ollama | latest | `curl -fsSL https://ollama.com/install.sh \| sh` (zstd 필요: `apt-get install -y zstd`) |
| 모델 | qwen2.5-coder:32b | `ollama pull qwen2.5-coder:32b` (qwen2.5:27b는 존재하지 않음!) |

**한계:** Ollama는 직렬 서버 — 동시 요청을 보내도 내부적으로 순차 처리.
BP_WORKERS 올려도 이득 없음. **candidate당 ~25분, GPU 사용률 14%.** 돈 낭비.

### Option B: vLLM (배치 처리, 빠름) — ✅ 추천

vLLM은 동시 요청을 GPU 배치로 묶어 처리 → WORKERS와 함께 쓰면 **5~10배 빠름**.

#### 검증 조합 (2026-06-17 실전 검증)

| 구성 요소 | 버전 | 비고 |
|-----------|------|------|
| RunPod 템플릿 | **PyTorch 2.4.0** | 가장 안정적 |
| Python | **3.11** | 템플릿 기본 포함 |
| PyTorch | **2.4.0+cu124** | 템플릿 기본 포함 (건드리지 말 것!) |
| vLLM | **0.23.0** | `pip install vllm` (자동으로 맞는 버전 설치) |
| 모델 | **Qwen/Qwen2.5-14B-Instruct** | ~27.5GB VRAM. A40에 딱 맞음 |

> ⚠️ **Qwen2.5-27B는 A40에서 OOM** — 14B를 쓸 것.
> ⚠️ PyTorch를 직접 설치/교체하면 높은 확률로 꼬임. 템플릿 기본 PyTorch 유지.

#### vLLM 서버 기동

```bash
nohup vllm serve Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 16384 \
    --gpu-memory-utilization 0.90 \
    > /workspace/vllm.log 2>&1 &

tail -f /workspace/vllm.log
# "Application startup complete" 나올 때까지 대기 (첫 실행: 모델 다운로드 포함 ~10분)
# CUDA graph 컴파일 포함 시 추가 수 분 소요
```

> ⚠️ **`--max-model-len 16384` 필수!**
> generate_batch.py가 `max_tokens=8000`을 요청함. 프롬프트 토큰까지 합치면 8192 초과.
> 8192로 하면 **400 Bad Request** 폭탄 맞음. (실전에서 검증된 함정)

#### vLLM 안 될 때 디버깅

| 증상 | 원인 / 해결 |
|------|-------------|
| `maximum context length is 8192` (400) | `--max-model-len 16384` 누락 → 재시작 |
| `OutOfMemoryError` / `Free memory ... less than desired` | GPU에 이전 프로세스 잔존 → `nvidia-smi --query-compute-apps=pid --format=csv,noheader \| xargs -r kill -9` 후 재시작 |
| 27B 모델 OOM | A40 48GB에 bf16 27B 안 올라감 → 14B로 변경 |
| vLLM PID가 1번 (컨테이너 메인) | vLLM 전용 템플릿에서 kill하면 컨테이너 죽음 → PyTorch 템플릿 사용 |
| `torch.cuda.is_available() = False` | PyTorch가 CPU 빌드 → 템플릿 기본 PyTorch 유지, 직접 설치 금지 |
| Pod restart 후 코드 사라짐 | `/workspace`는 유지되지만 확인 필요. `git clone` 다시 |

---

## 2. generate_batch.py 실행

### 환경변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BP_LM_URL` | `http://127.0.0.1:1234/v1` | LLM 서버 엔드포인트 |
| `BP_LM_MODEL` | (빈 문자열 = 서버 기본) | 모델 지정 (vLLM: `Qwen/Qwen2.5-14B-Instruct`) |
| `BP_LM_API_KEY` | (빈 문자열) | API 키 (Gemma 템플릿 등에서 필요) |
| `BP_WORKERS` | `1` | 서브시스템 동시 생성 워커 수 |

### vLLM으로 실행 (배치, WORKERS=12) — ✅ 추천

```bash
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_WORKERS=12 \
BP_SKIP_AUDIT=1 \
nohup python generate_batch.py --seeds all --per-seed 50 \
    >> /workspace/gen.log 2>&1 &
```

> **WORKERS 가이드 (A40 48GB, 14B 모델):**
>
> | WORKERS | tokens/s | GPU 사용률 | 비고 |
> |---------|----------|-----------|------|
> | 3 | ~54 | 100% | 안전 기본값 |
> | 5 | ~85 | 100% | |
> | 7 | ~120 | 100% | |
> | 10 | ~165 | 100% | |
> | **12** | **~199** | **100%** | **최적 (서브시스템 12~13개와 일치)** |
> | 15+ | ~199 | 100% | 추가 이득 없음 (GPU 배치 포화) |
>
> - WORKERS=12가 서브시스템 수(12~13개)와 일치 → 한 candidate의 모든 서브시스템을 동시 생성
> - `BP_SKIP_AUDIT=1`: RunPod에서 build123d(CAD) 설치 불필요. 로컬에서 audit 재판정
> - 7~8B 모델 → WORKERS=15~20까지 가능

### Ollama로 실행 (직렬, WORKERS=1) — 느림

```bash
BP_LM_URL=http://127.0.0.1:11434/v1 \
BP_WORKERS=1 \
nohup python generate_batch.py --seeds all --per-seed 8 \
    >> /workspace/gen.log 2>&1 &
```

---

## 3. 모니터링

```bash
# 진행률 (가장 유용)
cat 30_model/curation/batch_checkpoint.json

# 실시간 로그
tail -f /workspace/gen.log

# vLLM 서버 로그 (throughput, 에러 확인)
tail -f /workspace/vllm.log

# 프로세스 생존 확인
ps aux | grep generate_batch
```

---

## 4. 중단 & 이어하기

```bash
# 중단
kill $(pgrep -f generate_batch)

# 이어하기 — checkpoint에서 재개
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_WORKERS=12 \
BP_SKIP_AUDIT=1 \
nohup python generate_batch.py --seeds all --per-seed 50 --resume \
    >> /workspace/gen.log 2>&1 &
```

`--resume`은 batch_checkpoint.json의 `done` 값부터 이어서 진행.
checkpoint는 candidate 1개 완료될 때마다 자동 저장됨.

---

## 5. 완료 후: 로컬 CAD audit → Git push → LoRA 학습

### 5-1. RunPod 결과 다운로드

`BP_SKIP_AUDIT=1`로 돌렸으므로 CAD audit은 로컬에서 재판정한다.

```bash
# RunPod에서: 결과 압축 & 다운로드
cd /workspace/Blueprint_npu_portable
tar czf /workspace/batch_results.tar.gz 20_dataset/seeds_generated/ 30_model/curation/
# Pod 웹 터미널에서 다운로드하거나 scp
```

### 5-2. 로컬 CAD audit 재판정

build123d가 설치된 로컬에서 전체 audit 실행:

```bash
# 풀 audit (320개 × ~13초 ≈ 70분)
python run_local_audit.py

# 특정 seed만
python run_local_audit.py --seed robot_arm

# 결과 확인
python batch_monitor.py
```

> **seed별 차등 FoS 기준 (auto_decision):**
> - cubesat: keep ≥ 3.0, good ≥ 10, excellent ≥ 25
> - robot_arm: keep ≥ 0.15, good ≥ 0.5, excellent ≥ 3.0
> - tiltrotor: keep ≥ 0.6, good ≥ 3.0, excellent ≥ 10
> - small_launch_vehicle: keep ≥ 0.5, good ≥ 2.5, excellent ≥ 10
> - long_range_recon_wing: keep ≥ 0.5, good ≥ 1.0, excellent ≥ 1.8
> - haptic_glove: keep ≥ 0.8, good ≥ 5.0, excellent ≥ 20
>
> Keep 내에서 Grade A/B/C 등급으로 상대 품질 구분.
> LoRA 학습 시 A ×3, B ×2, C ×1로 가중 반복.

### 5-3. Git push

```bash
git add 20_dataset/seeds_generated/ 30_model/curation/
git commit -m "batch: N candidates via vLLM Qwen2.5-14B (audit complete)"
git push
```

### 5-4. LoRA 학습 (RunPod에서)

배치 완료 후 vLLM을 죽이고 GPU를 학습용으로 전환:

```bash
# 1. vLLM 종료 (GPU 메모리 해제)
pkill -f vllm
sleep 5
nvidia-smi  # 메모리 해제 확인

# 2. 학습 의존성 설치
pip install transformers peft datasets bitsandbytes accelerate trl

# 3. gate check (현재 keep+reject 수 확인)
cd /workspace/Blueprint_npu_portable
python 30_model/train_lora.py

# 4. LoRA 학습 (keep+reject >= 300이면 시험 학습 가능)
python 30_model/train_lora.py --train

# 4. 결과 push
git add 30_model/lora_out/
git commit -m "lora: trial adapter from 300 candidates"
git push
```

> **학습 게이트:** keep+reject 합산 기준
> - 300 rows = 시험 LoRA (현재 271 keep + 12 reject = 283, **17개 부족**)
> - 1000 rows = 본격 LoRA
>
> **Grade 가중치:** A등급 ×3, B등급 ×2, C등급 ×1 반복 학습 (고품질 예제 강조)
>
> A40 48GB + QLoRA + 300 rows → **약 30분~1시간**, 추가 비용 ~$0.50

---

## 6. 비용 추정 (RunPod A40 $0.46/hr)

| 구성 | candidate당 시간 | 300개 총 시간 | 비용 |
|------|-----------------|-------------|------|
| Ollama + WORKERS=1 | ~25분 | ~125시간 | ~$57.5 |
| vLLM + WORKERS=3 | ~2분 | ~10시간 | ~$4.6 |
| **vLLM + WORKERS=12** | **~50초** | **~4.5시간** | **~$2.0** |
| LoRA 학습 (300 rows) | — | ~0.5~1시간 | ~$0.25~0.50 |

→ vLLM + WORKERS=12 → **Ollama 대비 ~60배 빠름**. 실전 검증 완료 (199 tokens/s).

---

## 7. 삽질 방지 체크리스트

- [ ] RunPod 템플릿: **PyTorch 2.4.0** (vLLM 전용 템플릿 ❌ — PID 1 문제)
- [ ] 디스크: **50GB 이상** (모델 + 코드 + 결과)
- [ ] `--max-model-len 16384` 확인 (8192 ❌)
- [ ] 모델: Qwen2.5-**14B** (27B는 OOM)
- [ ] PyTorch 건드리지 않기 (템플릿 기본 유지)
- [ ] `BP_WORKERS=12` (14B 최적, Ollama에서는 효과 없음)
- [ ] `BP_SKIP_AUDIT=1` (RunPod에서 CAD audit 스킵 → 로컬에서 재판정)
- [ ] nohup + `>>` 로 실행 (창 닫아도 안전)
