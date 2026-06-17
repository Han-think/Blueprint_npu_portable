# 10_execution/cad — 정밀 CAD 백엔드

`geometry_ops`(설계 의도) → **build123d(OCC 솔리드)** → root-part mock assembly STL + feature-rich 2D 도면(SVG).
three.js 근사가 아닌 진짜 솔리드. 3D는 root part를 분리 배치하고, 2D는 내부 feature, service access, interface cue, op callout을 표시.

## 옵션 백엔드 (portable 유지)
- 정밀 빌드는 `build123d` 필요: `pip install build123d` (OCC 커널 cadquery-ocp 포함)
- 미설치 시 빌더가 안내 후 종료. 기존 `ui/Minimal.html` 의 three.js 근사 뷰어가 fallback.

## 스크립트
| 파일 | 역할 |
|------|------|
| `build_solid.py <seed>` | geometry_ops + part_tree + assembly.json → root-part mock assembly STL → `output/<seed>/<seed>.stl` |
| `build_drawing.py <seed>` | schema_v6 geometry_ops + part_tree → 2D 3면 feature projection → `output/<seed>/<seed>_drawing.svg` |
| `assembly_interference_audit.py --all` | placed AABB/manifest/print_readiness → collision·clearance·mate·print-block review report |

## 현재 상태 (5 seed 전체 완료)
root part별 local solid를 만들고 seed별 교육용 mock assembly layout으로 배치.

| seed | root parts placed | STL 부피 | triangles |
|------|-------------------|----------|-----------|
| cubesat | 4/4 | 479K mm³ | 5058 |
| tiltrotor | 5/5 | 214K mm³ | 9100 |
| robot_arm | 5/5 | 871K mm³ | 5260 |
| small_launch_vehicle | 5/5 | 876K mm³ | 5070 |
| long_range_recon_wing | 5/5 | 766K mm³ | 3844 |

- ✅ STL(3D/프린터) + SVG(2D 3면) 각 5개, 전부 부피>0 매니폴드
- ✅ STL은 root part separated / cutaway-exploded educational mock assembly 형태
- ✅ SVG는 `TOP / FRONT CUTAWAY / SIDE INTERFACE`와 내부 feature/operation callout/part-tree internals/assembly service cues를 표시
- ✅ 적용 op: box·cylinder·shell(hollow)·pocket·boss·drill·channel·pattern·loft(approx)·engrave(approx)·chamfer·fillet
- anchor 토큰: `center · face_±X/Y/Z · corners_4 · internal · axis_Z · edge_vertical/top` (+ offset_mm)
- 잔여 스킵: 일부 fillet/chamfer 엣지 충돌 — 부피·root part 배치·매니폴드엔 영향 없음

## 체결·조립 + 비용 리포트 (cubesat 파일럿)
schema_v6 불변 유지 + 별도 확장 계약 `00_contract/assembly_spec.schema.json`.

- `seeds/<seed>/assembly.json` — fasteners(M2/PIN·위치·clearance/tap홀·토크) + joints(mate·공차) + hardware_bom
- `build_solid.py` — assembly.json 의 fastener hole 정밀 천공 (clearance Ø+0.2 / tap Ø-0.4 / through)
- `assembly_report.py <seed>` — 효율/비용 성과 + 아쉬운 점 자동 리포트:
  - cubesat 실측: 부품 5→4(-20%), 조립 18→9단계(-50%), 하드웨어 M2×8+PIN2×2, 조립시간 -50%
  - 아쉬운 점 → 온톨로지 태그(PARTIAL_INTEGRATE/DECOUPLE/RISK)로 다음 재설계 입력
  - 진화 연결: judgment_causal 의 guardrail 과 대응

## 5 seed 효율/비용 성과 (assembly_report)
| seed | 부품 | 조립단계 | 하드웨어 |
|------|------|----------|----------|
| cubesat | 5→4 (-20%) | 18→9 (-50%) | M2×8, PIN2×2 |
| tiltrotor | 8→5 (-38%) | 24→13 (-46%) | M3×8, PIN3×2 |
| robot_arm | 9→5 (-44%) | 28→15 (-46%) | M4×4, M3×10 |
| small_launch_vehicle | 10→5 (-50%) | 30→16 (-47%) | M3×12 |
| long_range_recon_wing | 10→5 (-50%) | 29→15 (-48%) | M3×6, PIN2×2 |

## 정밀화 로드맵 (진화)
1. ✅ anchor 좌표 보강 → 전체 op 조립
2. ✅ 체결/조립 스키마 + fastener hole 천공 + 비용·효율 리포트
3. ✅ assembly.json 5 seed 전체 확장 + STL 나사홀 천공 + 5 seed 리포트
4. ✅ root-part mock assembly 배치 + cutaway/exploded preview
5. ✅ 2D 도면을 feature-rich schema projection으로 전환 — 솔리드 정밀 투영은 다음 단계
6. boolean op(subtract) 정밀 지원 → 컷어웨이 품질 고도화
7. STL → slicer_job → gcode (3D프린터 실출력)
8. ✅ AABB 기반 실조립 간섭/clearance/print-block audit v1 → `assembly_interference_report.json` (정밀 mating face는 다음)
9. 리포트 아쉬운점 → 모델 재설계 → 재빌드 자동 루프 (closed-loop 개선)

## 출력물
`output/` 는 생성물 — 버전관리 제외 권장.

## 3D 뷰 연결
생성 STL 을 `ui/Minimal.html`(STL 로더 보유)이 로드하면 근사 아닌 정밀 표시.
(서버: `start.ps1` → http://127.0.0.1:8080)
