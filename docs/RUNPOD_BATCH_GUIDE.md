# RunPod 배치 생성 가이드

generate_batch.py를 유료 GPU 서버(RunPod 등)에서 돌릴 때의 환경 셋업,
vLLM 전환, 병렬 워커 설정, LoRA 학습까지 다룬다.

---

## 0. 원샷 복붙 스크립트 (vLLM, 2026-06-23 검증)

> Pod 생성 후 터미널 열고 아래를 **순서대로 복붙**하면 끝.
> 템플릿: **RunPod PyTorch 2.4.0** / GPU: **A40 48GB**
> 디스크: **Container 20GB + Volume 50GB** (섹션 0-1 참고)

```bash
# ── Step 1: 코드 클론 ──
cd /workspace
# Public repo:
git clone https://github.com/Han-think/Blueprint_ipex_portable.git
# Private repo (토큰 필요):
# git clone https://<GITHUB_TOKEN>@github.com/Han-think/Blueprint_ipex_portable.git
cd Blueprint_ipex_portable

# ── Step 2: 의존성 황금조합 설치 ──
# 템플릿 기본 패키지가 너무 새로움 -> 검증된 버전으로 다운그레이드 필수!
pip install torch==2.4.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124
pip install vllm==0.5.5
pip install transformers==4.44.2

# outlines 잔여 파일 정리 (새 버전 -> 0.0.46 다운그레이드 시 types/ 폴더 잔류)
pip uninstall outlines -y
rm -rf /usr/local/lib/python3.11/dist-packages/outlines/
pip install outlines==0.0.46

# pyairports 스텁 (0.0.1 버전에 AIRPORT_LIST 없음)
python -c "
import os
pkg = '/usr/local/lib/python3.11/dist-packages/pyairports'
os.makedirs(pkg, exist_ok=True)
open(os.path.join(pkg, '__init__.py'), 'w').close()
with open(os.path.join(pkg, 'airports.py'), 'w') as f: f.write('AIRPORT_LIST = []\n')
print('pyairports stub OK')
"

# pip 캐시 정리 (Container disk 절약)
pip cache purge
rm -rf /root/.cache/pip/

# ── Step 3: 모델 캐시를 Volume에 받기 (필수!) ──
export HF_HOME=/workspace/hf_cache

# ── Step 4: vLLM 서버 기동 ──
nohup vllm serve Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 24576 \
    --gpu-memory-utilization 0.90 \
    > /workspace/vllm.log 2>&1 &

# ── Step 5: 서버 올라올 때까지 대기 ──
tail -f /workspace/vllm.log
# "Application startup complete" 뜨면 Ctrl+C
# 첫 실행: 모델 다운로드(~28GB) + CUDA graph 컴파일 = 5~10분
```

```bash
# ── Step 6: 배치 생성 시작 ──
cd /workspace/Blueprint_ipex_portable
export HF_HOME=/workspace/hf_cache
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_WORKERS=12 \
BP_SKIP_AUDIT=1 \
nohup python generate_batch.py --seeds all --per-seed 50 \
    >> /workspace/gen.log 2>&1 &

# ── Step 7: 30초 후 로그 확인 ──
sleep 30 && tail -20 /workspace/gen.log
```

```bash
# ── Step 8: 완료 후 Git push ──
cd /workspace/Blueprint_ipex_portable
git add 30_model/curation/
git commit -m "batch: N candidates via vLLM Qwen2.5-14B"
git push
```

---

## 0-1. RunPod 디스크 구조 & 저장 위치 가이드

RunPod Pod에는 **두 개의 독립된 디스크**가 있다. 혼동하면 용량 부족으로 서버가 죽는다.

### 디스크 구조

```
/ (Container Disk)              /workspace (Network Volume)
+-- /usr/local/lib/ (pip pkgs)  +-- Blueprint_ipex_portable/ (코드)
+-- /root/.cache/ (기본 캐시)     +-- hf_cache/ (HF_HOME -> 모델 캐시)
+-- /tmp/                       +-- vllm.log, gen.log
+-- OS + CUDA toolkit           +-- batch_results.tar.gz
```

| 디스크 | 마운트 | 용도 | 권장 크기 | 유지 |
|--------|--------|------|----------|------|
| Container Disk | `/` | OS, pip 패키지, CUDA | **20GB** | Pod 삭제 시 사라짐 |
| Network Volume | `/workspace` | 코드, 모델 캐시, 데이터 | **50GB** | Pod 재시작해도 유지 |

### 핵심 설정: `HF_HOME=/workspace/hf_cache`

HuggingFace 모델 캐시 기본 경로는 `/root/.cache/huggingface/` (Container Disk).
Qwen2.5-14B가 ~28GB인데 Container Disk에 받으면 **즉시 디스크 풀**.

```bash
export HF_HOME=/workspace/hf_cache   # 반드시 vllm serve 전에 실행!
```

이렇게 하면 모델이 Network Volume에 다운로드되어:
- Container Disk 보호 (pip 패키지만 담당)
- Pod 재시작 후에도 모델 캐시 유지 (재다운로드 불필요)

### 용량 계산

| 항목 | 위치 | 크기 |
|------|------|------|
| pip 패키지 (torch, vllm 등) | Container `/` | ~15GB |
| Qwen2.5-14B 모델 | Volume `/workspace/hf_cache/` | ~28GB |
| 코드 + git | Volume `/workspace/Blueprint.../` | ~1GB |
| 배치 출력 (curation_log 등) | Volume `/workspace/Blueprint.../` | ~2GB |
| **Container 합계** | | **~15GB / 20GB** |
| **Volume 합계** | | **~31GB / 50GB** |

### 디스크 비용 & 운영 전략

| 디스크 | 비용 | 과금 방식 | Pod 종료 시 |
|--------|------|----------|------------|
| Container Disk | **무료** (Pod 가격 포함) | GPU 시간당 요금에 포함 | **삭제됨** (휘발) |
| Network Volume | **~$0.07/GB/월** | Pod 꺼도 계속 과금 | **유지됨** (영구) |

- 50GB Volume = 월 ~$3.5 상시 과금 (Pod 안 써도)
- Container는 Pod 시작할 때마다 빈 상태로 생성 -> pip 매번 재설치 (황금조합 3분)
- Volume은 모델 캐시 + 코드 + 결과물 보존 -> Pod 재시작해도 재다운로드 불필요

**왜 Volume에 몰아넣나?** Qwen 14B 모델이 28GB. Container에 두면 Pod 재시작마다
10분 + 28GB 재다운로드. Volume에 두면 한번 받고 계속 재사용.

**비용 절약 팁:**
- 배치 완료 후 당분간 안 쓸 거면 Volume 삭제 -> 과금 멈춤
- 다음에 필요하면 Volume 새로 만들고 모델 재다운로드 (~10분이면 끝)
- 자주 쓸 예정이면 Volume 유지가 편함 (월 $3.5)

### Private 레포 클론 (선택)

레포가 Private인 경우 RunPod에서 클론할 때 GitHub Personal Access Token이 필요하다.

```bash
# 1. GitHub > Settings > Developer settings > Personal access tokens > Generate
# 2. 권한: repo (Full control of private repositories)
# 3. 클론 시 토큰 삽입:
git clone https://ghp_XXXXXXXXXXXX@github.com/Han-think/Blueprint_ipex_portable.git
```

> 토큰은 RunPod 터미널에서만 사용하고, 코드에 커밋하지 말 것.
> Pod을 다른 사람과 공유하지 않는다면 보안 위험 낮음.

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

#### 검증 조합 (2026-06-23 실전 검증, 황금조합)

| 구성 요소 | 버전 | 비고 |
|-----------|------|------|
| RunPod 템플릿 | **PyTorch 2.4.0** | 가장 안정적 |
| Python | **3.11** | 템플릿 기본 포함 |
| PyTorch | **2.4.0+cu124** | `pip install torch==2.4.0 --index-url .../cu124` |
| torchaudio | **2.4.0+cu124** | torch와 동일 버전 필수 |
| vLLM | **0.5.5** | `pip install vllm==0.5.5` (최신 버전 설치 금지!) |
| transformers | **4.44.2** | 5.x는 torchaudio/CUDA 충돌 |
| outlines | **0.0.46** | 반드시 rm -rf 후 재설치 (잔여 파일 문제) |
| 모델 | **Qwen/Qwen2.5-14B-Instruct** | ~27.5GB VRAM. A40에 딱 맞음 |

> **주의: `pip install vllm` 하면 안 됨!** 최신(0.23.0+)이 설치되어 PyTorch 2.7 끌어옴
> -> CUDA driver 호환 안 됨 -> 연쇄 에러. 반드시 `vllm==0.5.5` 고정.
>
> **주의: transformers 5.x 설치 금지!** torchaudio import -> libcudart.so.13 요구 -> 충돌.
>
> **주의: Qwen2.5-27B는 A40에서 OOM** -- 14B를 쓸 것.
>
> 전체 설치 순서는 섹션 0 원샷 스크립트 참고.

#### vLLM 서버 기동

```bash
nohup vllm serve Qwen/Qwen2.5-14B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 24576 \
    --gpu-memory-utilization 0.90 \
    > /workspace/vllm.log 2>&1 &

tail -f /workspace/vllm.log
# "Application startup complete" 나올 때까지 대기 (첫 실행: 모델 다운로드 포함 ~10분)
# CUDA graph 컴파일 포함 시 추가 수 분 소요
```

> **`--max-model-len 24576` 필수!**
> generate_batch.py가 `max_tokens=12000`을 요청함 (3차 배치부터 child별 geometry 강화로 증가).
> 프롬프트 토큰까지 합치면 16384 초과할 수 있음. 24576이면 안전.
> 8192나 16384로 하면 **400 Bad Request** 폭탄 맞음.

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
> | WORKERS | tokens/s | GPU 사용률 | VRAM | 비고 |
> |---------|----------|-----------|------|------|
> | 3 | ~54 | 100% | ~60% | 안전 기본값 |
> | 5 | ~85 | 100% | ~70% | |
> | 7 | ~120 | 100% | ~75% | |
> | 10 | ~165 | 100% | ~80% | |
> | **12** | **~199** | **100%** | **~85%** | **최적 (서브시스템 12~13개와 일치)** |
> | 15 | ~199 | 100% | ~90% | 한계치 근접, 이득 없음 |
> | 16+ | OOM 위험 | - | >90% | KV cache 부족 -> 요청 거부 |
>
> **왜 12가 최적인가?**
> - 각 candidate는 서브시스템 12~13개. WORKERS=12면 한 candidate의 모든 서브시스템 동시 생성
> - WORKERS=15 이상은 GPU 배치 포화 -> tokens/s 증가 없이 VRAM만 더 소비
> - 2026-06-23 실측: GPU 88%, VRAM 85% (WORKERS=12) -> 15는 돌아가지만 여유 거의 없음
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
cd /workspace/Blueprint_ipex_portable
tar czf /workspace/batch_results.tar.gz 20_dataset/seeds_generated/ 30_model/curation/
# Pod 웹 터미널에서 다운로드하거나 scp
```

### 5-2. 로컬 CAD audit 재판정

build123d가 설치된 로컬에서 HOLD 행에 FoS 계산:

```bash
# 방법 A: payload 기반 audit (추천 - HOLD 행만 처리, 빠름)
python audit_hold_rows.py
# curation_log의 HOLD 행 payload → temp package.json → CAD pipeline → FoS → KEEP/REJECT 전환
# 76 HOLD × ~1.5초 ≈ 2분

# 방법 B: 폴더 기반 full audit (느림, 전체 재판정)
python run_local_audit.py --resync
# 기존 CAD 리포트 재읽기 → curation_log 업데이트

# 특정 seed만
python run_local_audit.py --seed robot_arm

# gate check
python 30_model/train_lora.py
```

> **audit_hold_rows.py vs run_local_audit.py:**
> - `audit_hold_rows.py`: curation_log payload에서 직접 CAD 파이프라인 실행. 폴더 매칭 불필요.
> - `run_local_audit.py --resync`: 기존 CAD output 리포트 재읽기. 새 리포트 없으면 효과 없음.
> - RunPod에서 `BP_SKIP_AUDIT=1`로 돌린 후에는 **audit_hold_rows.py가 정답**.

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
cd /workspace/Blueprint_ipex_portable
python 30_model/train_lora.py

# 4. LoRA 학습 (keep+reject >= 300이면 시험 학습 가능)
python 30_model/train_lora.py --train

# 4. 결과 push
git add 30_model/lora_out/
git commit -m "lora: trial adapter from 300 candidates"
git push
```

> **학습 게이트:** keep+reject 합산 기준
> - 300 rows = 시험 LoRA (현재 286 keep + 75 reject = 361, **통과**)
> - 1000 rows = 본격 LoRA
>
> **Grade 가중치:** A등급 ×3, B등급 ×2, C등급 ×1 반복 학습 (고품질 예제 강조)
>
> A40 48GB + QLoRA + 300 rows → **약 30분~1시간**, 추가 비용 ~$0.50

### 5-5. 역설계 분석 데이터 생성 (순방향 배치 완료 후)

기존 keep 블루프린트를 입력으로 7종 역설계 분석 학습 데이터를 생성한다.
순방향(생성) + 역방향(분석) 데이터가 합쳐져야 진짜 설계 전문 모델이 된다.

```bash
# vLLM 서버 유지한 상태에서 역분석 생성
cd /workspace/Blueprint_ipex_portable
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
python generate_reverse.py --tasks all --max 100

# 특정 태스크만
python generate_reverse.py --tasks structural,thermal --seed cubesat --max 20

# 통계 확인
python generate_reverse.py --stats
```

> **7종 역설계 태스크:**
>
> | 태스크 | 분석 내용 |
> |--------|----------|
> | structural | 구조 취약점 + FEA 메시 힌트 + 보강 제안 |
> | thermal | 열경로 병목 + CFD 셋업 + 냉각 개선 |
> | dfa | 조립 효율 + Boothroyd 점수 + 부품 통합 |
> | fmea | 고장 모드 + RPN + 검사 계획 |
> | cost | 원가 동인 + VE 제안 + make/buy 분석 |
> | weight | 경량화 기회 + 토폴로지 존 + AM 전환 |
> | tolerance | 공차 체인 + 스택업 + GD&T 콜아웃 |
>
> train_lora.py가 reverse_log.jsonl을 자동으로 학습 데이터에 포함함.

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

## 7. 배치 품질 개선 이력

### 3차 배치 프롬프트 강화 (2026-06-23)

2차 배치에서 72/75 reject이 LOW-RES (child당 geometry_ops 부족)로 판명.
원인: "전체 12-24 ops" 규칙만 있고 child별 최소 ops 규칙 없어서 LLM이 p-001에 몰빵.

**수정 내역 (generate_batch.py):**

| 항목 | 2차 배치 | 3차 배치 |
|------|---------|---------|
| 최소 total ops | 8 | **16** |
| child별 최소 ops | 없음 | **4 (body+subtract+interface+finish)** |
| part_tree child 최소 | 2 | **5** |
| coordinate 분포 | "not all origin" | **child별 distinct 좌표, 2+ 영역** |
| max_tokens | 8000 | **12000** |
| max-model-len | 16384 | **24576** |
| 치수 현실성 | 없음 | **seed별 스케일 범위 명시** |

stage_issues 검증도 강화: S2에서 sparse target 분배 체크, S1에서 child 5개 미만 거부.

### 갭 분석 (어디가 부족한지 확인)

```bash
python generate_batch.py --gap-analysis
```

seed별 keep/reject/hold 수, grade A/B/C 분포, 부족한 곳을 자동 추천.

### 프롬프트 변형 (다양성 확보)

2차 배치부터 `PROMPT_VARIANTS`가 자동 적용된다. seed당 4-5개 시나리오를
라운드로빈으로 순환하여 동일 seed라도 다른 설계 의도의 결과물을 생산한다.

```bash
# 예: cubesat 5개 → 5개 variant 각 1회씩 적용
BP_LM_URL=http://127.0.0.1:8000/v1 \
BP_LM_MODEL=Qwen/Qwen2.5-14B-Instruct \
BP_WORKERS=12 BP_SKIP_AUDIT=1 \
python generate_batch.py --seeds cubesat --per-seed 5
```

### 아티팩트 점검 (교사모델 반복 패턴 확인)

```bash
python 30_model/train_lora.py --check-artifacts
```

seed별 프롬프트 고유성, assistant 응답 패턴 반복률, geometry_ops 분포를 출력한다.

### 검증셋 분리

train_lora.py가 seed별 마지막 2개 keep을 자동으로 val holdout으로 분리한다.
`--train` 시 eval loss가 50 step마다 출력되므로 과적합을 모니터링할 수 있다.

---

## 8. 삽질 방지 체크리스트

- [ ] RunPod 템플릿: **PyTorch 2.4.0** (vLLM 전용 템플릿 X -- PID 1 문제)
- [ ] 디스크: **Container 20GB + Volume 50GB** (섹션 0-1 참고)
- [ ] `export HF_HOME=/workspace/hf_cache` (모델을 Volume에 받기!)
- [ ] 황금조합 설치 완료 (섹션 0 Step 2)
- [ ] `pip install vllm` 절대 금지 -- `vllm==0.5.5` 고정
- [ ] `pip install transformers` 절대 금지 -- `transformers==4.44.2` 고정
- [ ] outlines rm -rf 후 `outlines==0.0.46` 설치
- [ ] pyairports 스텁 생성 완료
- [ ] `--max-model-len 24576` 확인 (16384 이하 X - max_tokens=12000 + 프롬프트)
- [ ] 모델: Qwen2.5-**14B** (27B는 OOM)
- [ ] `BP_WORKERS=12` (14B 최적, Ollama에서는 효과 없음)
- [ ] `BP_SKIP_AUDIT=1` (RunPod에서 CAD audit 스킵 -- 로컬에서 재판정)
- [ ] nohup + `>>` 로 실행 (창 닫아도 안전)
- [ ] 완료 후 `pip cache purge && rm -rf /root/.cache/` (Container disk 정리)
