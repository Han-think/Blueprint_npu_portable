"""
analysis_estimate.py -- first-order analytical estimates (NOT a solver)
=======================================================================

Reads output/<name>/assembly_structure.json (part AABBs + placements) and,
if present, cfd/cfd_meta.json, then computes coarse aero / structural /
thermal estimates so the evolution loop has an analysis signal long before
a real CFD/FEA solver exists.

HONEST LIMIT: empirical proxies and first-order ratios only — for shape
trend and comparison, never absolute performance or certification.

Outputs:
  output/<name>/analysis_report.json

Usage:
  python analysis_estimate.py <name>        # name = seed or <seed>_generated
  python analysis_estimate.py --all         # the six curated seeds
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import solve_fea
import solve_cfd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "10_execution" / "cad" / "output"
SEED_LIST = ["cubesat", "tiltrotor", "robot_arm", "small_launch_vehicle",
             "long_range_recon_wing", "haptic_glove"]
EXTERNAL_FLOW_SEEDS = {"long_range_recon_wing", "tiltrotor", "small_launch_vehicle"}

# 발열 파트 라벨 → 공칭 전력(W) (경험적 가정값, 절대값 아님)
POWER_W = {
    "battery": 15, "motor": 40, "esc": 12, "avionics": 8, "controller": 8,
    "payload": 10, "actuator": 14, "electronics": 8, "reaction": 6, "antenna": 3,
}

# 재료 1차 물성: (allowable_MPa, density_g_per_mm3, fdm_knockdown).
# 교육용 근사값이며 인증/규격값이 아니다. FDM 출력은 층간 접착 약화로 knockdown.
MATERIAL = {
    "pla": (55, 0.00124, 0.45), "petg": (45, 0.00127, 0.45),
    "abs": (38, 0.00104, 0.45), "asa": (40, 0.00107, 0.45),
    "nylon": (55, 0.00114, 0.50), "tpu": (25, 0.00121, 0.50),
    "aluminum": (240, 0.00270, 1.0), "al6061": (240, 0.00270, 1.0),
    "steel": (350, 0.00785, 1.0), "titanium": (800, 0.00451, 1.0),
}
DEFAULT_MATERIAL = "petg"
SEED_MATERIAL = {
    "cubesat": "aluminum", "small_launch_vehicle": "aluminum",
    "tiltrotor": "petg", "long_range_recon_wing": "petg",
    "robot_arm": "petg", "haptic_glove": "tpu",
}
LOAD_FACTOR = 3.0    # 핸들링/기동 가정 하중계수 (보수적 교육용)
G_ACCEL = 9.81       # m/s^2
FOS_TARGET = 1.5     # 1차 사이징 목표 안전계수


def resolve_material(name: str, structure: dict) -> str:
    mat = (structure.get("material") or SEED_MATERIAL.get(base_seed(name), DEFAULT_MATERIAL))
    return str(mat).lower().strip()


def clamp(v, lo=0, hi=100):
    return int(round(max(lo, min(hi, v))))


def base_seed(name: str) -> str:
    return name[:-len("_generated")] if name.endswith("_generated") else name


def load_structure(name: str):
    p = OUT / name / "assembly_structure.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def assembly_extent(parts):
    """전체 어셈블리 union AABB 크기 [x,y,z]."""
    mn = [float("inf")] * 3
    mx = [float("-inf")] * 3
    for sp in parts:
        c = sp.get("placement_translation_mm") or [0, 0, 0]
        s = sp.get("bbox_mm") or [0, 0, 0]
        for i in range(3):
            mn[i] = min(mn[i], c[i] - s[i] / 2)
            mx[i] = max(mx[i], c[i] + s[i] / 2)
    if mn[0] == float("inf"):
        return [0, 0, 0]
    return [round(mx[i] - mn[i], 1) for i in range(3)]


def aero_estimate(name, parts):
    """외부유동 seed만: 세장비(fineness) 기반 유선형 근사."""
    if base_seed(name) not in EXTERNAL_FLOW_SEEDS:
        return None
    ext = assembly_extent(parts)
    length = max(ext)
    cross = sorted(ext)[:2]            # 두 단면 치수
    max_cross = max(cross) if max(cross) > 0 else 1.0
    fineness = round(length / max_cross, 2)
    frontal_area_mm2 = round(cross[0] * cross[1], 0)
    # Cd 근사: 너무 뭉툭(fineness<2) 높음, 3~8 최적, 너무 가늘면(>12) 표면마찰↑
    if fineness < 2:
        cd = 0.9
    elif fineness <= 8:
        cd = 0.10 + (3 - min(fineness, 3)) * 0.15
    else:
        cd = 0.12 + (fineness - 8) * 0.02
    drag_index = round(cd * frontal_area_mm2 / 1000.0, 1)
    score = clamp(100 - abs(fineness - 5) * 11 - (40 if fineness < 2 else 0))
    findings = []
    if fineness < 2:
        findings.append(f"aero: bluff body (fineness {fineness}) — streamline along flow axis to cut drag")
    elif fineness > 12:
        findings.append(f"aero: over-slender (fineness {fineness}) — skin-friction dominated, check structural span")
    return {
        "applicable": True, "fineness_ratio": fineness,
        "frontal_area_mm2": frontal_area_mm2, "cd_estimate": round(cd, 3),
        "drag_index": drag_index, "score": score, "findings": findings,
    }


def structural_estimate(parts, joints_by_part):
    """파트별 세장비 → Euler 좌굴 proxy. 지지 인터페이스 없으면 위험 가중."""
    worst = []
    risk = 0
    for sp in parts:
        s = sorted(sp.get("bbox_mm") or [1, 1, 1])
        longest = s[2]
        min_cross = s[0] if s[0] > 0 else 1.0
        sln = round(longest / min_cross, 1)
        supported = joints_by_part.get(sp.get("part_id"), 0) >= 2
        if sln > 18 and not supported:
            risk += 1
            worst.append((sp.get("part_id"), sln))
    score = clamp(100 - risk * 22 - max(0, (max((w[1] for w in worst), default=0) - 18)) * 1.5)
    findings = [f"structure: {pid} slenderness {sln} with <2 supports — buckling risk, add bracing/support"
                for pid, sln in worst[:3]]
    return {"buckling_risk_parts": risk, "worst": worst[:5], "score": score, "findings": findings}


def sizing_estimate(parts, material_name):
    """1차 사이징: 각 부재를 자중 분포하중 캔틸레버로 보고 근원 굽힘응력 σ=M/S 와
    재료 허용응력 대비 안전계수(FoS)를 계산한다. 치수가 하중을 견디는지 '실측'한다.
    HONEST LIMIT: 자중·가정 하중계수 기반 1차 계산 — 인증 구조해석이 아니다."""
    allow_mpa, dens, knock = MATERIAL.get(material_name, MATERIAL[DEFAULT_MATERIAL])
    allowable = allow_mpa * knock  # 출력 약화 반영 허용응력 (MPa = N/mm^2)
    # 전체 어셈블리 질량(자중 합) + 최장 스팬: 주 하중경로 부재는 시스템 질량을 반력한다고 본다.
    def _vol(sp):
        d = sp.get("bbox_mm") or [1, 1, 1]
        return float(d[0]) * float(d[1]) * float(d[2])
    total_mass_kg = sum(_vol(sp) * dens / 1000.0 for sp in parts if sp.get("bbox_mm"))
    max_extent = max((max(sp.get("bbox_mm") or [1]) for sp in parts), default=1.0)
    sys_force_N = LOAD_FACTOR * total_mass_kg * G_ACCEL
    rows = []
    for sp in parts:
        s = sorted([float(v) for v in (sp.get("bbox_mm") or [1, 1, 1])])
        b, h, L = s[0], s[1], s[2]      # b=얇은쪽, h=단면 깊이, L=최장(보 길이)
        if L < 1 or h < 0.5 or b < 0.5:
            continue
        self_mass_kg = b * h * L * dens / 1000.0
        primary = L >= 0.4 * max_extent  # 스팬이 긴 주 부재: 시스템 하중을 외팔보 끝에서 반력
        if primary:
            moment_Nmm = sys_force_N * L                    # 시스템 하중 외팔보 끝하중 M=F·L
            load_model = "carried_system_load"
        else:
            moment_Nmm = LOAD_FACTOR * self_mass_kg * G_ACCEL * L / 2.0  # 자중 분포하중
            load_model = "self_weight"
        section_modulus = b * h * h / 6.0                  # 직사각 단면계수 S = b·h^2/6 (mm^3)
        sigma_mpa = moment_Nmm / section_modulus if section_modulus > 0 else 9e9
        fos = round(allowable / sigma_mpa, 2) if sigma_mpa > 0 else 999.0
        rows.append({"part_id": sp.get("part_id"), "label": sp.get("label"), "load_model": load_model,
                     "section_b_mm": round(b, 1), "section_h_mm": round(h, 1), "len_mm": round(L, 1),
                     "bending_stress_mpa": round(sigma_mpa, 2), "fos": fos, "ok": fos >= FOS_TARGET})
    if not rows:
        return {"applicable": False, "score": 80, "findings": []}
    worst = sorted(rows, key=lambda r: r["fos"])[:5]
    worst_fos = worst[0]["fos"]
    under = [r for r in rows if not r["ok"]]
    score = clamp(min(worst_fos, 2.0) / 2.0 * 100)         # FoS 2.0→100, 1.5→75, 1.0→50
    findings = [f"sizing: {r['label'] or r['part_id']} FoS {r['fos']} (<{FOS_TARGET}) — "
                f"bending {r['bending_stress_mpa']}MPa vs allowable {round(allowable, 1)}MPa; "
                f"raise section depth/ribs/wall" for r in under[:3]]
    return {"applicable": True, "material": material_name, "allowable_mpa": round(allowable, 1),
            "load_factor": LOAD_FACTOR, "fos_target": FOS_TARGET, "worst_fos": worst_fos,
            "under_sized_parts": len(under), "worst": worst, "score": score, "findings": findings,
            "total_mass_kg": round(total_mass_kg, 4), "density_g_mm3": dens}


def thermal_estimate(parts):
    """발열 파트 전력 합 vs 외피 표면적 → 방열 여유 proxy."""
    total_w = 0.0
    surf_cm2 = 0.0
    for sp in parts:
        label = str(sp.get("label", "")).lower()
        s = sp.get("bbox_mm") or [0, 0, 0]
        surf_cm2 += 2 * (s[0] * s[1] + s[1] * s[2] + s[0] * s[2]) / 100.0
        for key, w in POWER_W.items():
            if key in label:
                total_w += w
                break
    if total_w <= 0:
        return {"applicable": False, "total_power_w": 0, "surface_cm2": round(surf_cm2, 0),
                "score": 80, "findings": []}
    index = round(surf_cm2 / total_w, 1)   # cm2 per W (높을수록 방열 여유)
    score = clamp(index * 4)               # ~25 cm2/W 면 100
    findings = []
    if index < 12:
        findings.append(f"thermal: only {index} cm2/W heat-rejection area — add radiator/vent/heatsink or spread heat sources")
    return {"applicable": True, "total_power_w": round(total_w, 0),
            "surface_cm2": round(surf_cm2, 0), "cm2_per_w": index, "score": score, "findings": findings}


def kinematic_estimate(parts, mates):
    """회전 mate(pin/hinge/revolute) 가동부가 0~90° swing 시 데이텀과 충돌 여유 proxy.
    swept_radius = 파트 최장/2, 부모와의 중심거리와 비교."""
    ROTARY = ("pin", "hinge", "revolute")
    by_id = {p.get("part_id"): p for p in parts}
    rows = []
    risk = 0
    for m in mates:
        if str(m.get("mate", "")).lower() not in ROTARY:
            continue
        a, b = by_id.get(m.get("part_a")), by_id.get(m.get("part_b"))
        if not a or not b:
            continue
        mover = a if max(a.get("bbox_mm") or [0]) <= max(b.get("bbox_mm") or [0]) else b
        anchor = b if mover is a else a
        s = sorted(mover.get("bbox_mm") or [1, 1, 1])
        swept_radius = round(s[2] / 2, 1)
        ca = mover.get("aabb_mm", {}).get("center_mm") or mover.get("placement_translation_mm") or [0, 0, 0]
        cb = anchor.get("aabb_mm", {}).get("center_mm") or anchor.get("placement_translation_mm") or [0, 0, 0]
        dist = round(sum((ca[i] - cb[i]) ** 2 for i in range(3)) ** 0.5, 1)
        anchor_half = (max(anchor.get("bbox_mm") or [1]) / 2)
        clear = round(dist - anchor_half - swept_radius, 1)
        ok = clear > -2.0   # 약간의 중첩은 mate 접촉 허용
        if not ok:
            risk += 1
        rows.append({"joint": m.get("id"), "mover": mover.get("part_id"),
                     "swept_radius_mm": swept_radius, "clearance_mm": clear, "ok": ok})
    if not rows:
        return {"applicable": False, "score": 80, "findings": []}
    score = clamp(100 - risk * 25)
    findings = [f"kinematic: {r['mover']} (joint {r['joint']}) sweep clearance {r['clearance_mm']}mm — may collide through motion range"
                for r in rows if not r["ok"]][:3]
    return {"applicable": True, "joints": rows, "score": score, "findings": findings}


def run_beam_fe(sizing: dict) -> dict | None:
    """실제 빔 FE로 가장 임계한 부재를 푼다(근사식이 아닌 K u = F 수치해). 결과를
    sizing 분석에 솔버 출처로 부착. 솔버 결과가 있으면 sizing의 권위 FoS가 된다."""
    if not sizing.get("applicable") or not sizing.get("worst"):
        return None
    w = sizing["worst"][0]
    b, h, L = w["section_b_mm"], w["section_h_mm"], w["len_mm"]
    mat = sizing.get("material", DEFAULT_MATERIAL)
    dens = sizing.get("density_g_mm3", MATERIAL[DEFAULT_MATERIAL][1])
    allowable = sizing.get("allowable_mpa", 20.0)
    E = solve_fea.E_MPA.get(mat, solve_fea.DEFAULT_E)
    w_self_N_per_mm = LOAD_FACTOR * (b * h * dens / 1000.0) * G_ACCEL   # 자중 분포하중
    tip = (LOAD_FACTOR * sizing.get("total_mass_kg", 0.0) * G_ACCEL
           if w.get("load_model") == "carried_system_load" else 0.0)
    res = solve_fea.solve_cantilever(b, h, L, E_mpa=E, allowable_mpa=allowable,
                                     w_N_per_mm=w_self_N_per_mm, tip_load_N=tip)
    if res.get("ok"):
        res["member"] = w.get("part_id")
        res["material"] = mat
    return res


def estimate(name: str) -> dict | None:
    structure = load_structure(name)
    if not structure:
        return None
    parts = structure.get("parts", []) or []
    mates = structure.get("mates", []) or []
    joints_by_part = {}
    for m in mates:
        for k in (m.get("part_a"), m.get("part_b")):
            if k:
                joints_by_part[k] = joints_by_part.get(k, 0) + 1

    material_name = resolve_material(name, structure)
    aero = aero_estimate(name, parts)
    structural = structural_estimate(parts, joints_by_part)
    sizing = sizing_estimate(parts, material_name)
    thermal = thermal_estimate(parts)
    kinematic = kinematic_estimate(parts, mates)

    # STEP 4: 실제 빔 FE 솔버로 임계 부재 재해석 → sizing의 권위 FoS/출처 갱신.
    fea = run_beam_fe(sizing)
    if sizing.get("applicable"):
        if fea and fea.get("ok"):
            sizing["fea"] = fea
            sizing["provenance"] = "solver:euler_bernoulli_beam_fe_numpy"
            sizing["solver_fos"] = fea["fos"]
            sizing["solver_max_stress_mpa"] = fea["max_bending_stress_mpa"]
            sizing["score"] = clamp(min(fea["fos"], 2.0) / 2.0 * 100)   # 솔버 FoS가 점수 권위
            if fea["fos"] < FOS_TARGET:
                sizing.setdefault("findings", []).append(
                    f"sizing(FE): {fea.get('member')} solved FoS {fea['fos']} (<{FOS_TARGET}) "
                    f"max bending {fea['max_bending_stress_mpa']}MPa, tip defl {fea['tip_deflection_mm']}mm")
        else:
            sizing["provenance"] = "proxy:analytic_bending"

    # STEP 4: 외부유동 CFD 솔버 가용성 탐지(없으면 aero proxy를 정직 표기).
    if aero and aero.get("applicable"):
        cfd = solve_cfd.run_cfd(OUT / name)
        aero["solver"] = cfd
        aero["provenance"] = ("solver:openfoam" if cfd.get("available") and cfd.get("status") != "driver_ready"
                              else "proxy:fineness_ratio (CFD solver_unavailable)")

    scores = [c["score"] for c in (aero, structural, sizing, thermal, kinematic) if c and c.get("score") is not None]
    overall = clamp(sum(scores) / len(scores)) if scores else 60
    findings = []
    for c in (aero, structural, sizing, thermal, kinematic):
        if c:
            findings += c.get("findings", [])
    status = "ok" if overall >= 70 else "watch" if overall >= 45 else "weak"

    loop = [f"Analytical first-order estimate for {name}: {status}, score {overall}/100 (trend-level, not a solver)."]
    loop += [f"- {f}" for f in findings[:6]]
    loop.append("- These are empirical proxies for shape comparison; do not claim certified performance.")

    return {
        "schema": "blueprint_analysis_estimate_v1",
        "name": name,
        "seed": base_seed(name),
        "disclaimer": "First-order analytical proxy (aero fineness / structural slenderness / "
                      "self-weight bending FoS / thermal area-per-watt). Computed from geometry + "
                      "assumed load factor and material allowable — NOT a CFD/FEA solver or certified "
                      "structural analysis. Shape/sizing trend and comparison only.",
        "assembly_extent_mm": assembly_extent(parts),
        "aero": aero or {"applicable": False, "reason": "internal/non-flow seed"},
        "structural": structural,
        "sizing": sizing,
        "thermal": thermal,
        "kinematic": kinematic,
        "score": overall,
        "status": status,
        "findings": findings[:10],
        "loop_feedback": "\n".join(loop),
    }


def run(name: str) -> int:
    rep = estimate(name)
    if not rep:
        print(f"[{name}] no assembly_structure.json — run export_step_assembly first")
        return 1
    (OUT / name / "analysis_report.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    a = rep["aero"]
    sz = rep["sizing"]
    print(f"[{name}] analysis {rep['status']} {rep['score']}/100 · "
          f"aero {a.get('fineness_ratio', 'n/a') if a.get('applicable') else 'n/a'} · "
          f"struct risk {rep['structural']['buckling_risk_parts']} · "
          f"sizing FoS {sz.get('solver_fos', sz.get('worst_fos', 'n/a')) if sz.get('applicable') else 'n/a'}"
          f"[{'FE' if sz.get('fea') else 'proxy'}/{sz.get('material', '')}] · "
          f"thermal {rep['thermal'].get('cm2_per_w', 'n/a')}cm2/W")
    return 0


def main(argv):
    args = [a for a in argv[1:] if a]
    if not args:
        print("usage: python analysis_estimate.py <name> | --all")
        return 1
    names = SEED_LIST if args[0] == "--all" else [args[0]]
    rc = 0
    for n in names:
        rc |= run(n)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
