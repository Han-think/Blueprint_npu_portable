# Reference Asset Enrichment — 2026-07-02

16개 seed 전체에 레퍼런스 CAD/엔지니어링 데이터를 보강하고, 검증·정제 후 git에 반영한 작업 기록.

## 목적

LLM이 geometry_ops를 생성할 때 참조할 seed별 설계 문법(design grammar)을 실물 CAD로 제공한다.
기존에는 6개 seed만 SCAD/STL 자료가 있었고, 신규 10개 seed는 비어 있거나 더미 수준이었다.
이번 작업으로 **16개 seed 전부가 실제 엔지니어링 CAD 레퍼런스를 보유**하게 됐다.

## 수집 경로

### 자동 크롤 (`tools/crawl_reference_assets.py`)

| 소스 | 라이선스 | 대상 seed |
|------|---------|----------|
| FreeCAD/FreeCAD-library | LGPL | pump, engine, gearbox (크랭크샤프트, 베어링, 펌프, 기어모터) |
| OpenFOAM tutorials | GPL-3.0 | pump(믹서/로터), cold_plate(CHT 지오메트리) |
| RocketPy | MIT | rocket (추력곡선/비행데이터/탱크질량 CSV 23종) |
| NopSCADlib | GPL-3.0 | battery, cnc, underwater (SCAD) |
| openscad/MCAD | LGPL | gearbox, hydraulic (SCAD) |

### GrabCAD 수동 다운로드 (65 zip, 자동 크롤 불가 영역)

| 폴더 | zip 수 | 채택 파일 |
|------|--------|----------|
| centrifugal_pump | 11 | 12 (Ebara CMR100T, KSB Etanorm, Hidrostal F10K, 어셈블리 컷어웨이) |
| liquid_cold_plate | 7 | 13 (Alfa Laval M3/M6/M10/M15 판형 열교환기, cold plate) |
| inline 6 engine | 17 | 5 (직렬6 레이아웃, 엔진블록 어셈블리, 마그네토) |
| rocket engine | 30 | 14 (연소실, 가스발생기, 터보펌프 컷어웨이, 아크젯, 랩터 메시) |

## 검증·정제 내역

1. **STEP 헤더 검증** — 34개 전부 `ISO-10303-21` 헤더 확인, STL 8개 binary 유효, IGES 7개 유효
2. **오분류 제거** — 로켓 seed에 섞인 제트엔진 부품(터빈/컴프레서 팬 등) 62개 삭제
3. **엔진 타입 정제** — inline-6 seed에서 V6, 3기통, 모터사이클(CBR600) 엔진 제거
4. **GitHub 제한 대응** — 100MB 초과 3개 제거(407MB TurboRock, 143MB GSwirl, 102MB Honda), 50MB+ 잔여 0개
5. **IGS 중복 제거** — 동일 모델 STEP 존재 시 IGES 삭제 (-76MB)
6. **무관 파일 제거** — pump에 잡힌 지붕 철판/플랫바/플랜지너트, engine에 잡힌 서보모터 등

### 파일명 정규화 규칙

- 소문자 + 언더스코어, 더블 언더스코어(`__`) 금지
- 부품 설명 우선, 출처 힌트 후행 (예: `ebara_cmr100t_full.stp`, `openfoam_rushton_stirrer_6blade.obj`)
- 키릴 문자 영문화: `КС` → `combustion_chamber`, `Сборка ТНА разрез` → `turbopump_assy_cutaway`, `СБ фГ` → `gas_generator_assy`
- 크롤 경로 인코딩 제거: `Mechanical_Parts__Bearings__608ZZ...` → `bearing_608zz.step`

## 최종 인벤토리 (450 파일, 467MB)

| Seed | 파일 수 | 주요 콘텐츠 |
|------|--------|------------|
| haptic_glove | 72 | DOGlove SCAD/STL |
| robot_arm | 64 | ARMada SCAD/STL |
| centrifugal_pump | 44 | GrabCAD 펌프 어셈블리 + FreeCAD 배관 + OpenFOAM 믹서 |
| liquid_rocket_engine_academic | 37 | 연소실/터보펌프/가스발생기 STEP + RocketPy CSV |
| cubesat | 31 | Hiapo 구조체 + PROVES PCB |
| small_launch_vehicle | 31 | SCAD/STL + OpenVSP |
| cnc_axis_carriage | 29 | NopSCADlib 리니어/레일/스테퍼 |
| inline_6_engine_gasoline | 29 | 직렬6 레이아웃 + 크랭크샤프트 + 베어링 |
| inline_6_engine_diesel | 29 | gasoline 공유 부품 |
| gearbox_reducer | 18 | 기어모터 + involute 기어 SCAD |
| liquid_cold_plate | 18 | Alfa Laval 판형 열교환기 + OpenFOAM CHT |
| long_range_recon_wing | 12 | OpenVSP 기체 |
| tiltrotor | 12 | SCAD/STL |
| underwater_sealed_sensor_housing | 12 | O-ring/하우징 SCAD |
| hydraulic_manifold | 9 | MCAD 블록/포트 SCAD |
| battery_pack_module | 8 | NopSCADlib 셀홀더/커넥터 SCAD |

확장자 분포: STL 176, SCAD 81, STEP/STP 61, OBJ 34, FCStd 29, CSV 24, VSP3 22, 문서 21, IGS 2

## 데이터 정책 (2-tier)

- **레퍼런스 자산 (`20_dataset/reference_assets/`) = 공개** — git 추적. 학습용 참조 자료이며 재배포 목적 아님
- **민감 데이터 (`20_dataset/local_restricted/`) = 비공개** — gitignore. 추진제 화학(O/F비, Isp), 점화 시퀀스, 챔버 사이징, 인젝터/냉각채널 설계 수치
- GrabCAD 자산은 원작자 라이선스가 제각각 → `_index.jsonl`에서 `license_gate: blocked_until_license_review` 상태 유지, 라이선스 리뷰 전까지 학습 사용 차단
- 대용량 로그(`curation_log.jsonl`, `reverse_log.jsonl` >100MB)도 gitignore — 직접 전송으로 공유

## 고용량 정책

- 현재: 일반 git (50MB+ 파일 0개, 총 467MB) — RunPod에서 `git clone` 1-2분 수준으로 문제없음
- 향후 레퍼런스가 1GB를 넘으면: Git LFS 또는 HuggingFace dataset/외부 스토리지 + `setup_runpod.sh` 다운로드 단계로 전환
- 민감 데이터 보호 강화 검토 예정: git-crypt 또는 age 파일 암호화

## Git 이력 노트

레퍼런스 추가~정제 과정의 중간 커밋 4개에 100MB+ 파일(최대 407MB)이 포함되어 GitHub push가 거부됨.
→ `git reset --soft`로 4커밋을 `1675b04` 1커밋으로 squash하여 대용량 파일을 히스토리에서 완전히 제거 후 push 성공.
브랜치: `update-runpod-guide`, 리모트 반영 완료 (a66ed36..1675b04).

## 남은 작업

1. `reference_feature_cards.jsonl` 갱신 — 신규 자산 반영한 seed별 design grammar 카드
2. GrabCAD 자산 라이선스 리뷰 → 통과분 `--allow-training-use` 전환
3. 기존 6 seed 실물 CAD 보강 (cubesat 태양전지판/ADCS, tiltrotor 나셀 틸트기구, recon wing 기체구조)
4. 민감 데이터 암호화 방안 (git-crypt/age) 도입 검토
5. RunPod 신규 10 seed 스모크 테스트 → LoRA 학습 준비
