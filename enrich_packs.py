"""enrich_packs.py — keep 286개에서 자동 추출하여 subsystem pack 보강

Usage:
  python enrich_packs.py              # 전체 seed 보강 + 통계 출력
  python enrich_packs.py --dry-run    # 변경 없이 추출 결과만 확인
  python enrich_packs.py --seed robot_arm  # 특정 seed만
"""
import json, argparse
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parent
PACKS = REPO / "20_dataset" / "packs"
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"

SEEDS = ["cubesat", "robot_arm", "tiltrotor", "small_launch_vehicle",
         "long_range_recon_wing", "haptic_glove"]

SEED_CONTEXT = {
    "cubesat": {
        "scale": "100x100x340mm (3U CubeSat)",
        "environment": "LEO vacuum, -40 to +80C thermal cycling, radiation",
        "loads": "launch vibration 20g, deployment shock, solar pressure",
    },
    "robot_arm": {
        "scale": "80-400mm per link, 600-1200mm reach",
        "environment": "industrial floor, IP54, 10-40C ambient",
        "loads": "payload 2-10kg at tip, joint torque 5-50Nm, 10k+ cycles",
    },
    "tiltrotor": {
        "scale": "200-1500mm wingspan, 50-300mm fuselage dia",
        "environment": "outdoor flight, -20 to +50C, rain/dust/salt",
        "loads": "rotor thrust 20-200N, tilt servo 5-30Nm, 3g maneuvering",
    },
    "small_launch_vehicle": {
        "scale": "100-500mm dia, 500-2000mm length (display model)",
        "environment": "indoor display, handling loads, educational use",
        "loads": "static display 1g, handling 2g, no flight loads",
    },
    "long_range_recon_wing": {
        "scale": "800-3000mm wingspan, 100-250mm chord",
        "environment": "outdoor flight, -10 to +45C, dust/humidity",
        "loads": "wing bending 3g, servo 2-8Nm, catapult launch 15g",
    },
    "haptic_glove": {
        "scale": "150-250mm palm, 60-100mm per finger segment",
        "environment": "human contact, skin-safe, 20-35C, sweat/moisture",
        "loads": "finger force 2-10N, cable tension 5-30N, 100k+ flex cycles",
    },
}

UNIVERSAL_CRITERIA = [
    {
        "id": "geometry_grounding",
        "title": "P0 to Geometry Grounding",
        "criteria": [
            {
                "criterion": "p0_feature_mapping",
                "weight": 14,
                "good": "P0 internal_feature_targets appear as part_tree children and geometry_ops ids or targets.",
                "bad": "P0 lists features but geometry_ops are generic boxes at the origin.",
            },
            {
                "criterion": "coordinate_distribution",
                "weight": 12,
                "good": "Most geometry_ops include args.at coordinates distributed across the local subsystem volume.",
                "bad": "Geometry is stacked at [0,0,0] or lacks coordinates.",
            },
            {
                "criterion": "non_box_feature_variety",
                "weight": 10,
                "good": "Uses drill, pocket, boss, channel, pattern_polar, fillet, chamfer — not just boxes.",
                "bad": "Only box and cylinder ops with no subtractive or finishing features.",
            },
            {
                "criterion": "per_child_geometry_density",
                "weight": 15,
                "good": "Every part_tree child has 4+ dedicated geometry_ops (body+subtract+interface+finish).",
                "bad": "Some children have 0-1 ops (LOW-RES). All detail concentrated on primary body.",
            },
        ],
    },
    {
        "id": "datum_tolerance",
        "title": "Datum & Tolerance Management",
        "criteria": [
            {
                "criterion": "primary_datum_evidence",
                "weight": 8,
                "good": "A primary datum feature (flat, bore, or pin) is explicitly named and placed.",
                "bad": "No datum reference — assembly alignment is uncontrolled.",
            },
            {
                "criterion": "interface_fit_class",
                "weight": 8,
                "good": "Adjacent interfaces include fit_class (H7/h6, LC2) and stack_up_mm.",
                "bad": "Interfaces have no tolerance or fit specification.",
            },
            {
                "criterion": "assembly_sequence_defined",
                "weight": 10,
                "good": "cad_brief includes ordered assembly_sequence with tool, torque, datum per step.",
                "bad": "No assembly order — build sequence is ambiguous.",
            },
        ],
    },
]


def load_keeps():
    rows = [json.loads(l) for l in CURATION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if r.get("decision") == "keep"]


def load_pack(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_pack(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_seed_patterns(keeps, seed):
    seed_keeps = [r for r in keeps if r.get("seed") == seed]
    if not seed_keeps:
        return {}

    op_counter = Counter()
    child_names = Counter()
    target_names = Counter()
    op_per_subsystem = defaultdict(lambda: Counter())
    dims = {"envelope_x": [], "envelope_y": [], "envelope_z": [], "mass_g": []}

    for r in seed_keeps:
        parts = (r.get("payload") or {}).get("parts", [])
        for p in parts:
            bp = p.get("blueprint", {})
            label = p.get("label", "")

            ops = bp.get("geometry_ops", [])
            for o in ops:
                op_type = o.get("op", "")
                op_counter[op_type] += 1
                op_per_subsystem[label][op_type] += 1
                t = o.get("target", "")
                if isinstance(t, list):
                    for ti in t:
                        if isinstance(ti, str) and ti:
                            target_names[ti] += 1
                elif isinstance(t, str) and t:
                    target_names[t] += 1

            children = (bp.get("part_tree") or {}).get("children", [])
            for c in children:
                name = c.get("name", "")
                if name:
                    child_names[name] += 1

            cb = bp.get("cad_brief", {})
            env = cb.get("envelope_mm", [])
            if isinstance(env, list) and len(env) == 3:
                dims["envelope_x"].append(env[0])
                dims["envelope_y"].append(env[1])
                dims["envelope_z"].append(env[2])
            mass = cb.get("mass_est_g")
            if isinstance(mass, (int, float)) and mass > 0:
                dims["mass_g"].append(mass)

    return {
        "n_keeps": len(seed_keeps),
        "op_types": op_counter,
        "child_names": child_names,
        "target_names": target_names,
        "op_per_subsystem": dict(op_per_subsystem),
        "dims": dims,
    }


def match_pack_to_patterns(pack, patterns):
    """Find which keep subsystems match this pack."""
    sub = pack.get("subsystem", {})
    pack_id = sub.get("id", "")
    pack_tokens = set(_tokenize(f"{pack_id} {sub.get('discipline','')} {sub.get('function','')} "
                                f"{' '.join(sub.get('evidence_features', []))}"))

    op_sub = patterns.get("op_per_subsystem", {})
    matches = []
    for label, ops in op_sub.items():
        label_tokens = set(_tokenize(label))
        overlap = len(pack_tokens & label_tokens)
        if overlap >= 2:
            matches.append((label, overlap, ops))
    matches.sort(key=lambda x: -x[1])
    return matches[:5]


def _tokenize(s):
    out = []
    for w in str(s or "").lower().replace("_", " ").replace("/", " ").replace("-", " ").split():
        w = "".join(c for c in w if c.isalnum())
        if len(w) >= 3:
            out.append(w)
    return out


def build_boundary_note(seed, pack):
    ctx = SEED_CONTEXT.get(seed, {})
    sub = pack.get("subsystem", {})
    disc = sub.get("discipline", "")
    func = sub.get("function", "")

    parts = [f"Subsystem scale: {ctx.get('scale', 'N/A')}."]
    parts.append(f"Environment: {ctx.get('environment', 'N/A')}.")
    parts.append(f"Design loads: {ctx.get('loads', 'N/A')}.")

    if "thermal" in disc or "thermal" in func.lower():
        parts.append("Thermal design: include heat source/sink zones with W or degC values in verify.boundary_conditions.thermal_zones.")
    if "struct" in disc or "frame" in func.lower() or "rail" in func.lower():
        parts.append("Structural: include fixture_points with [x,y,z] and type (fixed/pinned) in verify.boundary_conditions.")
    if "mech" in disc or "actuator" in func.lower() or "linkage" in func.lower():
        parts.append("Mechanism: include joint travel range, preload, and cycle life in cad_brief.")
    if "avionics" in disc or "electronics" in func.lower() or "sensor" in func.lower():
        parts.append("Electronics: include EMI shielding, thermal dissipation path, and connector keying in design.")

    return " ".join(parts)


def enrich_evidence_features(pack, patterns, pack_matches):
    """Add missing evidence_features from keep data."""
    sub = pack.get("subsystem", {})
    existing = set(f.lower().replace("_", " ") for f in sub.get("evidence_features", []))

    candidates = Counter()
    for label, _, ops in pack_matches:
        for child_name, count in patterns.get("child_names", {}).items():
            tokens = _tokenize(child_name)
            pack_tokens = set(_tokenize(f"{sub.get('id','')} {sub.get('discipline','')} {sub.get('function','')}"))
            if any(t in pack_tokens for t in tokens):
                normalized = child_name.lower().replace(" ", "_")
                if normalized not in existing and len(normalized) > 3:
                    candidates[normalized] += count

    new_features = []
    seen = set(existing)
    for f, cnt in candidates.most_common(8):
        if cnt < 3:
            break
        norm = f.lower().replace("-", "_").replace(" ", "_")
        if norm not in seen:
            seen.add(norm)
            new_features.append(f)
        if len(new_features) >= 5:
            break
    return new_features


def enrich_criteria(pack, seed, patterns, pack_matches):
    """Add universal criteria if missing, plus seed-specific op-type criteria."""
    existing_ids = set()
    for doc in pack.get("criteria", []):
        existing_ids.add(doc.get("id", ""))

    added = []
    for uc in UNIVERSAL_CRITERIA:
        if uc["id"] not in existing_ids:
            added.append(uc)

    # seed-specific op-type criteria from keep data
    op_types = patterns.get("op_types", Counter())
    top_ops = [op for op, _ in op_types.most_common(6) if op not in ("box", "cylinder")]
    if top_ops and "seed_op_signature" not in existing_ids:
        added.append({
            "id": "seed_op_signature",
            "title": f"{seed} Geometry Signature",
            "criteria": [
                {
                    "criterion": "expected_op_variety",
                    "weight": 10,
                    "good": f"Uses seed-characteristic ops: {', '.join(top_ops[:4])}. "
                            f"Subtractive features (drill/pocket/channel) and finishing (fillet/chamfer) both present.",
                    "bad": "Only basic box/cylinder ops. Missing subtractive or finishing features typical for this seed.",
                },
                {
                    "criterion": "dimensional_realism",
                    "weight": 10,
                    "good": f"Dimensions match {seed} scale: {SEED_CONTEXT.get(seed,{}).get('scale','N/A')}. "
                            f"Wall thickness, hole diameters, fillet radii are physically plausible.",
                    "bad": "Dimensions are placeholder (all 10mm) or unrealistic for the subsystem scale.",
                },
            ],
        })

    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    seeds = [args.seed] if args.seed else SEEDS
    keeps = load_keeps()
    print(f"[enrich] {len(keeps)} keep rows loaded\n")

    total_before = {"evidence": 0, "criteria": 0, "boundary": 0}
    total_after = {"evidence": 0, "criteria": 0, "boundary": 0}

    for seed in seeds:
        if not (PACKS / seed).exists():
            continue

        patterns = extract_seed_patterns(keeps, seed)
        if not patterns:
            print(f"[{seed}] no keep data, skipping")
            continue

        pack_files = sorted(f for f in (PACKS / seed).glob("*.json") if f.name != "skeleton.json")
        print(f"=== {seed} ({patterns['n_keeps']} keeps, {len(pack_files)} packs) ===")

        seed_before = {"evidence": 0, "criteria": 0, "boundary": 0}
        seed_after = {"evidence": 0, "criteria": 0, "boundary": 0}

        for pf in pack_files:
            pack = load_pack(pf)
            sub = pack.get("subsystem", {})
            existing_ev = len(sub.get("evidence_features", []))
            existing_cr = sum(len(d.get("criteria", [])) for d in pack.get("criteria", []))
            existing_bn = 1 if pack.get("boundary_note") else 0

            seed_before["evidence"] += existing_ev
            seed_before["criteria"] += existing_cr
            seed_before["boundary"] += existing_bn

            pack_matches = match_pack_to_patterns(pack, patterns)

            # 1. Enrich evidence_features (with dedup)
            new_features = enrich_evidence_features(pack, patterns, pack_matches)
            if new_features:
                sub.setdefault("evidence_features", []).extend(new_features)
            # dedup existing features
            seen_ef = set()
            deduped = []
            for f in sub.get("evidence_features", []):
                norm = f.lower().replace("-", "_").replace(" ", "_")
                if norm not in seen_ef:
                    seen_ef.add(norm)
                    deduped.append(f)
            sub["evidence_features"] = deduped

            # 2. Enrich criteria
            new_criteria = enrich_criteria(pack, seed, patterns, pack_matches)
            if new_criteria:
                pack.setdefault("criteria", []).extend(new_criteria)

            # 3. Add/update boundary_note (replace generic "educational display" notes too)
            bn = pack.get("boundary_note", "")
            if not bn or "educational display" in bn.lower():
                pack["boundary_note"] = build_boundary_note(seed, pack)

            new_ev = len(sub.get("evidence_features", []))
            new_cr = sum(len(d.get("criteria", [])) for d in pack.get("criteria", []))
            new_bn = 1 if pack.get("boundary_note") else 0

            seed_after["evidence"] += new_ev
            seed_after["criteria"] += new_cr
            seed_after["boundary"] += new_bn

            delta_ev = new_ev - existing_ev
            delta_cr = new_cr - existing_cr
            delta_bn = new_bn - existing_bn

            if delta_ev or delta_cr or delta_bn:
                changes = []
                if delta_ev: changes.append(f"+{delta_ev} evidence")
                if delta_cr: changes.append(f"+{delta_cr} criteria")
                if delta_bn: changes.append("+boundary_note")
                print(f"  {pf.name:35s} {' | '.join(changes)}")

                if not args.dry_run:
                    save_pack(pf, pack)

        print(f"  {'TOTAL':35s} evidence {seed_before['evidence']}→{seed_after['evidence']} | "
              f"criteria {seed_before['criteria']}→{seed_after['criteria']} | "
              f"boundary {seed_before['boundary']}→{seed_after['boundary']}")
        print()

        for k in total_before:
            total_before[k] += seed_before[k]
            total_after[k] += seed_after[k]

    print(f"{'='*60}")
    print(f"  ALL SEEDS: evidence {total_before['evidence']}→{total_after['evidence']} | "
          f"criteria {total_before['criteria']}→{total_after['criteria']} | "
          f"boundary {total_before['boundary']}→{total_after['boundary']}")
    if args.dry_run:
        print("  (dry-run: no files modified)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
