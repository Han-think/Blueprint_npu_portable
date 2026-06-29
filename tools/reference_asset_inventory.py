"""Rebuild and validate the reference asset inventory."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "20_dataset" / "reference_assets"
INDEX = ROOT / "_index.jsonl"
REPORT_JSON = ROOT / "_inventory_report.json"
REPORT_MD = ROOT / "_inventory_report.md"
ALLOWED = {
    ".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3",
    ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".json", ".jsonl", ".csv", ".txt", ".md",
}
CONTROL_DIRS = {"_incoming", "_quarantine", "_cache", "__pycache__"}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_index() -> list[dict[str, Any]]:
    rows = []
    if not INDEX.exists():
        return rows
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def asset_kind(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3"}:
        return "cad"
    if ext in {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}:
        return "image_or_drawing"
    return "metadata"


def main() -> int:
    rows = read_index()
    indexed_paths = {str(r.get("path", "")).replace("\\", "/"): r for r in rows}
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO)
        parts = set(path.relative_to(ROOT).parts)
        if parts & CONTROL_DIRS:
            continue
        if path.name in {
            "_index.jsonl",
            "_inventory_report.json",
            "_inventory_report.md",
            "sources.json",
            "seed_reference_targets.json",
            "RUN_REFERENCE_CRAWL.md",
            "README.md",
        }:
            continue
        if path.suffix.lower() not in ALLOWED:
            continue
        files.append(path)

    missing_from_index = []
    for path in files:
        rel = str(path.relative_to(REPO)).replace("\\", "/")
        if rel not in indexed_paths and path.name != "metadata.json":
            missing_from_index.append(rel)

    missing_on_disk = []
    for rel in indexed_paths:
        if rel and not (REPO / rel).exists():
            missing_on_disk.append(rel)

    by_seed = defaultdict(Counter)
    by_license = Counter()
    duplicate_hashes = defaultdict(list)
    duplicate_seeds = defaultdict(set)
    for row in rows:
        by_seed[row.get("seed", "unknown")][row.get("asset_kind", "unknown")] += 1
        by_license[row.get("license_status", "unknown")] += 1
        digest = row.get("sha256")
        if digest:
            duplicate_hashes[digest].append(row.get("path"))
            duplicate_seeds[digest].add(row.get("seed", "unknown"))
    duplicates = {
        h: p for h, p in duplicate_hashes.items()
        if len(p) > 1 and len(duplicate_seeds[h]) == 1
    }
    shared_across_seeds = {
        h: p for h, p in duplicate_hashes.items()
        if len(p) > 1 and len(duplicate_seeds[h]) > 1
    }

    report = {
        "schema": "blueprint_reference_asset_inventory_v1",
        "generated_at": now_iso(),
        "root": str(ROOT.relative_to(REPO)),
        "indexed_rows": len(rows),
        "disk_files": len(files),
        "by_seed": {seed: dict(counts) for seed, counts in sorted(by_seed.items())},
        "by_license_status": dict(by_license),
        "missing_from_index": missing_from_index,
        "missing_on_disk": missing_on_disk,
        "duplicate_hashes": duplicates,
        "shared_hashes_across_seeds": shared_across_seeds,
        "status": "pass" if not missing_on_disk and not duplicates else "watch",
        "notes": [
            "metadata.json files are seed profiles and are not required in _index.jsonl.",
            "blocked_until_license_review assets should guide prompts only after manual license review.",
        ],
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Reference Asset Inventory",
        "",
        f"Generated: {report['generated_at']}",
        f"Status: **{report['status']}**",
        "",
        f"- indexed rows: {report['indexed_rows']}",
        f"- disk files: {report['disk_files']}",
        "",
        "## By Seed",
        "",
        "| seed | cad | image_or_drawing | metadata |",
        "|---|---:|---:|---:|",
    ]
    for seed, counts in report["by_seed"].items():
        lines.append(
            f"| {seed} | {counts.get('cad', 0)} | {counts.get('image_or_drawing', 0)} | {counts.get('metadata', 0)} |"
        )
    lines += [
        "",
        "## License Status",
        "",
        *[f"- {k}: {v}" for k, v in report["by_license_status"].items()],
        "",
        "## Missing From Index",
        "",
        *[f"- {p}" for p in missing_from_index[:80]],
        "",
        "## Missing On Disk",
        "",
        *[f"- {p}" for p in missing_on_disk[:80]],
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(REPORT_JSON)
    print(REPORT_MD)
    print(f"[inventory] status={report['status']} indexed={len(rows)} disk_files={len(files)}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
