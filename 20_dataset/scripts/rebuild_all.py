"""
rebuild_all.py — 마스터 파이프라인: 소스 → 모든 산출물 한 방 재생성 + 검증
=========================================================================

소스(package/thinking/assembly)를 바꾼 뒤 이 한 줄이면 모든 파생 산출물이
의존 순서대로 재생성되고 전체가 검증된다. "진화 = 안전한 변화"의 척추.

사용:
    python rebuild_all.py          # 데이터 산출물 재생성 + 검증
    python rebuild_all.py --cad    # + STL/도면/대시보드(무거움)
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]            # 20_dataset
REPO = ROOT.parents[0]
SCRIPTS = ROOT / "scripts"
SEEDS = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]
PY = sys.executable


def run(args, label):
    print(f"\n▶ {label}")
    r = subprocess.run([PY, *args], cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (r.stdout or "").strip().splitlines()[-3:]
    for l in tail:
        print(f"   {l}")
    if r.returncode != 0:
        print(f"   ✗ 실패 (exit {r.returncode})")
        if r.stderr:
            print("   " + r.stderr.strip().splitlines()[-1])
        return False
    return True


def main(argv):
    cad = "--cad" in argv
    steps = []
    # 1. 판단 인과 (package → judgment_causal + eval)
    for s in SEEDS:
        steps.append(([str(SCRIPTS / "derive_judgment.py"), s], f"derive_judgment {s}"))
    # 2. 구체 도안 (part_spec)
    steps.append(([str(SCRIPTS / "derive_part_spec.py"), "--all"], "derive_part_spec --all"))
    # 3. 선호쌍 (preference)
    steps.append(([str(SCRIPTS / "derive_preference.py")], "derive_preference"))
    # 4. SFT 변환
    steps.append(([str(SCRIPTS / "build_sft.py")], "build_sft"))
    # 5. 대시보드 데이터
    steps.append(([str(REPO / "10_execution" / "cad" / "build_dashboard_data.py")], "build_dashboard_data"))
    # 6. (옵션) CAD
    if cad:
        for s in SEEDS:
            steps.append(([str(REPO / "10_execution" / "cad" / "build_solid.py"), s], f"build_solid {s}"))
            steps.append(([str(REPO / "10_execution" / "cad" / "build_drawing.py"), s], f"build_drawing {s}"))

    print("=== rebuild_all: 산출물 재생성 ===")
    for args, label in steps:
        if not run(args, label):
            print("\n[중단] 파이프라인 실패")
            return 1

    # 검증
    print("\n=== 검증 ===")
    ok = True
    for s in SEEDS:
        r = subprocess.run([PY, str(SEEDS_DIR(s))], cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace")
        mark = "OK" if r.returncode == 0 else "FAIL"
        if r.returncode != 0:
            ok = False
        print(f"   validate {s}: {mark}")
    for args, label in [([str(SCRIPTS / "validate_common.py")], "validate_common"),
                        ([str(SCRIPTS / "check_integrity.py")], "check_integrity")]:
        r = subprocess.run([PY, *args], cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace")
        mark = "OK" if r.returncode == 0 else "FAIL"
        if r.returncode != 0:
            ok = False
        print(f"   {label}: {mark}")
        for l in (r.stdout or "").strip().splitlines()[-2:]:
            print(f"      {l}")

    print("\n" + ("[OK] 전체 재생성 + 검증 통과 — 일관성 보증" if ok else "[FAIL] 검증 실패"))
    return 0 if ok else 1


def SEEDS_DIR(s):
    return ROOT / "seeds" / s / "validate.py"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
