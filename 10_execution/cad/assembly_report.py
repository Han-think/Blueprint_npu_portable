"""
assembly_report.py — 조립성·비용·효율 리포트 + 아쉬운 점 자동 도출
=================================================================

package(설계) + assembly(체결) + judgment_causal(판단) 을 종합해
baseline 대비 효율/비용 성과를 정량화하고, 개선할 "아쉬운 점"을 리포트한다.

사용:
    python assembly_report.py <seed>

정직한 한계: 비용은 재료(filament)+하드웨어+시간 추정. 절대 단가가 아닌 상대 비교/개선률에 유효.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEEDS = REPO / "20_dataset" / "seeds"

# 상대 비교용 추정 단가 (정직: 가정값)
FILAMENT_PER_G = 0.05      # 통화단위/g
HARDWARE_PER_PC = 0.10     # 나사 1개당
TIME_PER_STEP_MIN = 6      # 조립 단계당 분


def fnum(s, default=0.0):
    try:
        return float(s)
    except Exception:
        return default


def report(seed: str) -> int:
    pkg = json.loads((SEEDS / seed / "package.json").read_text(encoding="utf-8"))
    bp = pkg["schema_v6_blueprint"]
    cad = bp.get("cad_brief", {})
    pp = bp.get("print_profile", {})
    delta = pkg.get("assembly_delta", {})
    asm_path = SEEDS / seed / "assembly.json"
    asm = json.loads(asm_path.read_text(encoding="utf-8")) if asm_path.exists() else {}

    n_exist = len(pkg.get("existing_bom", []))
    n_redes = len(pkg.get("redesigned_bom", []))
    base_steps = delta.get("baseline_steps", 0)
    new_steps = delta.get("redesigned_steps", 0)
    access = delta.get("retained_service_access_points", [])
    hw = asm.get("hardware_bom", [])
    n_hw = sum(h.get("qty", 0) for h in hw)
    mass = cad.get("mass_est_g", 0)
    filament = pp.get("filament_g", mass)

    # 비용/효율 추정
    mat_cost = filament * FILAMENT_PER_G
    hw_cost = n_hw * HARDWARE_PER_PC
    asm_time = new_steps * TIME_PER_STEP_MIN
    base_time = base_steps * TIME_PER_STEP_MIN

    def pct(old, new):
        return f"{(old-new)/old*100:.0f}%" if old else "-"

    print(f"════ Assembly Report — {pkg['target']['vehicle_id']} ════")
    print(f"[부품/조립 효율]")
    print(f"  부품 그룹:   {n_exist} → {n_redes}  (절감 {pct(n_exist, n_redes)})")
    print(f"  조립 단계:   {base_steps} → {new_steps}  (절감 {pct(base_steps, new_steps)})")
    print(f"  서비스 접근점 유지: {len(access)}개")
    print(f"[하드웨어 BOM]")
    for h in hw:
        print(f"  {h['standard']:<6} × {h['qty']}")
    print(f"  총 {n_hw}개 · fasteners {len(asm.get('fasteners', []))}종 · joints {len(asm.get('joints', []))}")
    print(f"[비용/시간 추정 (상대비교)]")
    print(f"  재료: {filament}g → {mat_cost:.2f}")
    print(f"  하드웨어: {n_hw}개 → {hw_cost:.2f}")
    print(f"  조립시간: {base_time}분 → {asm_time}분  (절감 {pct(base_time, asm_time)})")
    print(f"  합계(추정): {mat_cost + hw_cost:.2f} + 조립 {asm_time}분")

    # ── 아쉬운 점 자동 도출 ──
    issues = []
    if new_steps > 8:
        issues.append((f"조립 단계 {new_steps}개 — 추가 통합/슬라이드 경로로 감소 여지", "PARTIAL_INTEGRATE"))
    if n_hw >= 8:
        issues.append((f"체결 하드웨어 {n_hw}개 — captive/snap 으로 나사 감소 검토", "DECOUPLE→snap"))
    highs = [r for r in bp.get("risk", []) if r.get("severity") == "high"]
    for r in highs:
        issues.append((f"[위험 {r['id']}] {r['desc'][:60]} → {r.get('mit','')[:50]}", "RISK"))
    if not access:
        issues.append(("서비스 접근점 미기재 — serviceability 검증 불가", "FAIL"))

    print(f"[아쉬운 점 / 개선 제안 — 다음 재설계 입력]")
    if not issues:
        print("  (자동 규칙상 특이사항 없음)")
    for msg, tag in issues:
        print(f"  • {msg}   <{tag}>")

    # 진화 연결: judgment_causal 의 trade_off 와 대응
    jc = SEEDS / seed / "judgment_causal.jsonl"
    if jc.exists():
        rows = [json.loads(l) for l in jc.read_text(encoding="utf-8").splitlines() if l.strip()]
        guards = [r["trade_off"]["guardrail"] for r in rows if r.get("trade_off", {}).get("guardrail")]
        print(f"[진화 연결] 지켜야 할 guardrail {len(guards)}개 (judgment_causal):")
        for g in guards[:3]:
            print(f"  - {g[:70]}")
    return 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("사용: python assembly_report.py <seed>"); return 1
    return report(args[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
