"""Build a per-seed context pack: only the criteria and sources that seed needs.

Usage:
  python build_context_pack.py <seed_name> [--max-kb 64]
  python build_context_pack.py --all

Selection rules (the "discernment" a local model will later replicate):
  1. criteria/*.json is included if applies_to contains "all" or the seed name.
  2. manifest sources are listed if their relevance intersects the seed name,
     "all_seeds", or the id of any included criteria file.
  3. Only citable sources contribute source_refs; reference-class sources are
     listed as local_reading_only and must never leave the machine.
  4. Extracted text under sources/_extracted/ is attached only if its book is
     relevant and the total pack stays under the size budget.

Output: 20_dataset/packs/<seed>.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 20_dataset/
SEEDS = [
    "long_range_recon_wing",
    "tiltrotor",
    "cubesat",
    "small_launch_vehicle",
    "robot_arm",
    "haptic_glove",
]


def load_criteria_for(seed: str) -> list[dict]:
    index = json.loads((ROOT / "criteria" / "criteria_index.json").read_text(encoding="utf-8"))
    selected = []
    for fname in index["criteria_files"]:
        doc = json.loads((ROOT / "criteria" / fname).read_text(encoding="utf-8"))
        applies = doc.get("applies_to", [])
        if "all" in applies or seed in applies:
            selected.append(doc)
    return selected


def load_sources_for(seed: str, criteria_ids: set[str]) -> tuple[list[dict], list[dict]]:
    manifest = json.loads((ROOT / "sources" / "manifest.json").read_text(encoding="utf-8"))
    wanted = {seed, "all_seeds"} | criteria_ids
    citable, local_only = [], []
    for src in manifest["sources"]:
        if not wanted & set(src.get("relevance", [])):
            continue
        entry = {
            "title": src["title"],
            "path": src["path"],
            "target_topics": src.get("target_topics", []),
        }
        if src.get("boundary"):
            entry["boundary"] = src["boundary"]
        (citable if src.get("citable") else local_only).append(entry)
    return citable, local_only


def attach_extracts(citable: list[dict], budget_bytes: int, used: int) -> list[dict]:
    extracts = []
    ext_root = ROOT / "sources" / "_extracted"
    if not ext_root.is_dir():
        return extracts
    stems = {Path(s["path"]).stem for s in citable}
    for book_dir in sorted(ext_root.iterdir()):
        if book_dir.name not in stems:
            continue
        for txt in sorted(book_dir.glob("*.txt")):
            body = txt.read_text(encoding="utf-8")
            if used + len(body) > budget_bytes:
                continue
            used += len(body)
            extracts.append({"book": book_dir.name, "label": txt.stem, "text": body})
    return extracts


def load_taxonomy_for(seed: str) -> dict:
    taxonomy = json.loads((ROOT / "criteria" / "subsystem_taxonomy.json").read_text(encoding="utf-8"))
    slice_ = taxonomy["seeds"].get(seed, {})
    used_disciplines = {s["discipline"] for s in slice_.get("required_subsystems", [])}
    return {
        "disciplines": {k: v for k, v in taxonomy["disciplines"].items() if k in used_disciplines},
        **slice_,
        "completeness_rule": "Every required_subsystem must appear in part_tree with at least one evidence_feature in geometry_ops; a missing subsystem is a scorecard failure, not a style issue.",
    }


def build(seed: str, max_kb: int) -> Path:
    criteria = load_criteria_for(seed)
    criteria_ids = {c["id"] for c in criteria}
    citable, local_only = load_sources_for(seed, criteria_ids)

    pack = {
        "schema": "blueprint_context_pack_v1",
        "seed": seed,
        "subsystem_taxonomy": load_taxonomy_for(seed),
        "policy": {
            "citable_sources_only_in_outputs": True,
            "local_reading_only_must_not_be_cited_or_exported": True,
        },
        "criteria": criteria,
        "citable_sources": citable,
        "local_reading_only": [{"title": s["title"], "target_topics": s["target_topics"]} for s in local_only],
    }
    used = len(json.dumps(pack, ensure_ascii=False))
    pack["extracts"] = attach_extracts(citable, max_kb * 1024, used)

    out_dir = ROOT / "packs"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{seed}.json"
    out.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _criterion_slice(criteria_docs: list[dict], wanted_ids: set[str]) -> list[dict]:
    """Return only the criterion entries of the criteria files named in wanted_ids."""
    out = []
    for doc in criteria_docs:
        if doc["id"] in wanted_ids:
            out.append({"id": doc["id"], "title": doc["title"], "criteria": doc["criteria"]})
    return out


def _connection_taxonomy_summary() -> dict:
    """connection_types.json을 family→[type:dof] 한 줄 요약으로 압축 (~0.8KB)."""
    path = ROOT / "criteria" / "connection_types.json"
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {
        "rule": "Name each inter-part interface with one of these connection types + its DOF + a numeric clearance, instead of a vague 'mount'.",
        "dof_codes": "0=fixed, 1R=revolute, 1T=prismatic, 1R1T=cylindrical, 3R=spherical",
        "families": {
            fam: [f"{t['type']}({t['dof']})" for t in types]
            for fam, types in doc.get("families", {}).items()
        },
    }


def build_micro_packs(seed: str, max_sub_kb: int = 10) -> list[Path]:
    """Emit packs/<seed>/skeleton.json and one micro-pack per required subsystem."""
    taxonomy = load_taxonomy_for(seed)
    criteria = load_criteria_for(seed)
    out_dir = ROOT / "packs" / seed
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    skeleton = {
        "schema": "blueprint_skeleton_pack_v1",
        "seed": seed,
        "pass": "PASS-0",
        "instruction": "Lay out the top-level part_tree with one node per required_subsystem, a global datum scheme, the overall envelope, and stub interfaces between subsystems. No detailed geometry.",
        "disciplines": taxonomy["disciplines"],
        "required_subsystems": [
            {k: s[k] for k in ("id", "discipline", "function", "evidence_features")}
            for s in taxonomy.get("required_subsystems", [])
        ],
        "completeness_rule": taxonomy["completeness_rule"],
        "global_judgment_summary": [
            {"id": d["id"], "criteria": [{"criterion": c["criterion"], "loop_feedback": c["loop_feedback"]} for c in d["criteria"]]}
            for d in criteria if d["id"] in ("geometry_grounding", "datum_tolerance", "assembly_integration")
        ],
        "connection_taxonomy": _connection_taxonomy_summary(),
    }
    if taxonomy.get("boundary_note"):
        skeleton["boundary_note"] = taxonomy["boundary_note"]
    sk_path = out_dir / "skeleton.json"
    sk_path.write_text(json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8")
    written.append(sk_path)

    for sub in taxonomy.get("required_subsystems", []):
        wanted = set(sub["criteria_refs"])
        citable, local_only = load_sources_for(seed, wanted)
        pack = {
            "schema": "blueprint_subsystem_pack_v1",
            "seed": seed,
            "pass": "PASS-1",
            "subsystem": sub,
            "instruction": "Design only this subsystem: P0 plan, part_tree children, 12-24 coordinate-bearing geometry_ops. Every evidence_feature must appear. Do not modify other subsystems or the global envelope.",
            "criteria": _criterion_slice(criteria, wanted),
            "citable_sources": [{"title": s["title"], "target_topics": s["target_topics"]} for s in citable],
        }
        if taxonomy.get("boundary_note"):
            pack["boundary_note"] = taxonomy["boundary_note"]
        body = json.dumps(pack, ensure_ascii=False, indent=2)
        if len(body) > max_sub_kb * 1024:
            pack.pop("citable_sources", None)
            body = json.dumps(pack, ensure_ascii=False, indent=2)
        p = out_dir / f"{sub['id']}.json"
        p.write_text(body, encoding="utf-8")
        written.append(p)
    return written


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    max_kb = 64
    if "--max-kb" in args:
        i = args.index("--max-kb")
        max_kb = int(args[i + 1])
        del args[i : i + 2]
    seeds = SEEDS if args[0] == "--all" else [args[0]]
    for seed in seeds:
        out = build(seed, max_kb)
        size = out.stat().st_size
        n = sum(len(c["criteria"]) for c in json.loads(out.read_text(encoding="utf-8"))["criteria"])
        print(f"{seed}: {out.name} ({size/1024:.1f} KB, {n} criteria)")
        for mp in build_micro_packs(seed):
            print(f"  micro: {mp.parent.name}/{mp.name} ({mp.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
