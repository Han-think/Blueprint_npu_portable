# RUN GUIDE — 직접 돌려보기 (익숙해지기용)

연결 모델: **LM Studio `openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix` 우선** (`127.0.0.1:1234/v1`)
fallback: **Ollama qwen3:8b → qwen2.5:7b → qwen3:4b** (`127.0.0.1:11434`)
한 번 돌리면 "workspace context + P0 사고엔진 + MRL-0.5 → 모델이 설계 판단/개선 후보 생성" 흐름을 직접 보게 된다.

> LM Studio는 사용자가 직접 실행한다. Blueprint는 이 repo 폴더를 folder-bound engineering workspace로 보고 local API만 호출한다.

---

## 4단계

### 1. LM Studio 서버 기동
1. LM Studio에서 `openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix` 모델을 로드.
2. Developer / Local Server를 켠다.
3. 기본 base URL: `http://127.0.0.1:1234/v1`

확인:
```
curl http://127.0.0.1:1234/v1/models
```

### 2. Ollama fallback 선택 기동
```
cd C:\Ollama-IPEX
ollama serve
```
- IPEX-LLM portable 패키지를 쓰면 그 폴더의 시작 스크립트(start-ollama 등)로 실행.
- 확인: 새 터미널에서 `ollama list` 또는 `curl http://127.0.0.1:11434/api/tags`

모델 받기 (처음 1회):
```
ollama pull qwen3:8b
```
- 받은 뒤 `ollama list` 에 `qwen3:8b` 보이면 OK.
- 메모리나 런타임 호환 문제가 있으면 `ollama pull qwen2.5:7b` 또는 `ollama pull qwen3:4b` 로 fallback.

### 3. Blueprint 서버 기동
```
cd C:\Ollama-IPEX\Blueprint_ipex_portable-main
.\start.ps1
```
- serve.py 가 `10_execution/ui` 를 서빙 + `/schema` `/validate` `/output` 제공.
- `/context-pack` 은 folder-bound engineering agent용 compact context를 제공.
- 브라우저가 자동으로 열린다 (http://127.0.0.1:8080).

### 4. 브라우저에서 생성
- 대시보드: `http://127.0.0.1:8080/` (5 seed 카드 · 3D/2D/STL)
- 생성 화면: `http://127.0.0.1:8080/Minimal.html`
  1. 상단에서 모델 선택 (LM Studio `openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix` 우선, Ollama fallback 가능)
  2. brief(설계 요구) 입력 — 예: "3U CubeSat 프레임, 보드 교체 접근성 유지"
  3. 생성 → P0 plan → geometry_ops → verify/risk → print profile 순서로 후보 생성
  4. keep/reject/hold/loop 선택
  5. `self-tune JSONL` export로 추후 LoRA/QLoRA 후보 데이터 축적

---

## 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `1234 무응답` | LM Studio server가 꺼짐 → LM Studio Developer server 시작 |
| LM Studio 모델 목록 비어있음 | LM Studio에서 `openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix` 모델 로드 |
| `11434 무응답` | Ollama fallback 서버 안 떠있음. LM Studio만 쓸 때는 무시 가능 |
| Minimal.html 에서 생성 안 됨 | `start.ps1` 로 연 서버에서 접속 (file:// 직접 열기 X), LM Studio/Ollama CORS 확인 |
| STL/2D 안 보임 | `start.ps1` 서버로 열어야 `/output` 접근 (정적 파일 직접 X) |
| 메모리 부족 | 더 작은 모델: `ollama pull qwen3:4b` 또는 `ollama pull qwen2.5:7b` 후 그걸 선택 |

---

## 이게 왜 "다음 단계"인가
지금 데이터·구조·무결성은 준비됨(SFT 184 + preference 169 + part_spec 24).
**LM Studio `openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix`를 이 폴더의 local engineering agent처럼 묶고**,
[workspace context → P0/MRL/scorecard → keep/reject → loop_feedback → self-tune JSONL] 흐름으로 실제 fine-tune 전 데이터 기반을 만든다.

---

## LoRA 학습 (GAP-3 2단계) — 데이터 게이트형

### 교사-학생 구조
- **교사(유지)**: gpt-oss-20B — 생성 + 판정. 튜닝 안 함.
- **학생(튜닝)**: qwen2.5:7b-instruct — 이 도메인(스키마 JSON 설계)만 잘하게 QLoRA. 가볍고 빠름.

### 데이터 누적 (자동)
- UI에서 good/bad 누를 때마다 serve.py `/persist-curation` 이 `30_model/curation/curation_log.jsonl` 에 **영구 누적**(중복 스킵, system/user/assistant 메시지 포맷 = 학습용).
- 현황 확인: `curl http://127.0.0.1:8080/curation-stats` 또는 Minimal.html LEARNING SIGNALS 의 "디스크 코퍼스 / LoRA 준비%".

### 폴백/학습 베이스 받기 (처음 1회, 사용자 액션)
```
ollama pull qwen2.5:7b-instruct
```
- Minimal.html 폴백 우선순위 정규식이 이걸 먼저 잡아 깔끔한 instruct 베이스가 된다(현재는 qwen2.5-coder:14b 로 잡힘).

### 학습 실행 (임계: 시험 300 / 본격 1000 rows)
```
python 30_model/train_lora.py            # 게이트 체크만 (안전, 학습 X)
python 30_model/train_lora.py --train    # >= 300 이면 시험 LoRA
```
- 임계 미만이면 "NOT ENOUGH DATA: N/300" 출력하고 학습 안 함 → 더 큐레이션.
- 실제 학습 시 필요: `pip install transformers peft datasets bitsandbytes accelerate trl`
- 산출: `30_model/lora_out/adapter` → GGUF 변환 후 Ollama/LM Studio 에 로드 → 학생 모델로 다음 세대 생성.

### 운용 원칙
- seed 균등(특정 seed 편중 금지), keep:reject ≈ 7:3.
- 500개 시험 → 효과 확인 → 1000개 본격. reject도 "회피" 신호로 학습된다.
