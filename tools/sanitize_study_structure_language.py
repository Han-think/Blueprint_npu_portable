"""Replace dummy/mock/display wording with academic study-structure wording.

This keeps safety boundaries, but avoids teaching the generator that important
engineering systems should be "dummies." The preferred vocabulary is academic,
conceptual, reference, non-operational, non-buildable, cutaway, study section,
and structure.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]

JSON_PATHS = [
    REPO / "20_dataset" / "seed_vehicles.json",
    *sorted((REPO / "20_dataset" / "packs").rglob("*.json")),
]

TEXT_PATHS = [
    REPO / "docs" / "ENGINEERING_EXPANSION_SEEDS_2026-06-27.md",
    REPO / "20_dataset" / "reference_assets" / "RUN_REFERENCE_CRAWL.md",
]

REPLACEMENTS = [
    ("Non-functional", "Non-operational academic"),
    ("non-functional", "non-operational academic"),
    ("Display Dummy", "Academic Study Section"),
    ("display dummy", "academic study section"),
    ("Display Shell", "Cutaway Study Shell"),
    ("display shell", "cutaway study shell"),
    ("Display Module", "Academic Study Module"),
    ("display module", "academic study module"),
    ("Display Cartridge", "Academic Study Cartridge"),
    ("display cartridge", "academic study cartridge"),
    ("Display Mock", "Academic Study Structure"),
    ("display mock", "academic study structure"),
    ("display-only", "academic non-operational"),
    ("Display-only", "Academic non-operational"),
    ("display only", "academic study only"),
    ("display/cutaway", "academic cutaway"),
    ("display grammar", "academic study grammar"),
    ("display/reference", "study/reference"),
    ("display-level", "study-level"),
    ("display model", "study model"),
    ("display Model", "study model"),
    ("display", "study"),
    ("Display", "Study"),
    ("educational display", "academic cutaway study"),
    ("Educational display", "Academic cutaway study"),
    ("educational mock", "academic study structure"),
    ("Educational mock", "Academic study structure"),
    ("mockup", "study assembly"),
    ("mock-up", "study assembly"),
    ("mock assembly", "study assembly"),
    ("mock", "reference structure"),
    ("Mock", "Reference Structure"),
    ("dummy", "reference article"),
    ("Dummy", "Reference Article"),
    ("dummies", "reference articles"),
    ("Dummies", "Reference Articles"),
    ("no pressure/ignition/flight capability", "academic boundary: no operational pressure, ignition, or flight-use instruction"),
    ("no pressure vessel claim", "no pressure-vessel certification claim"),
    ("no fluid service", "no operational fluid-service instruction"),
    ("no energetic device or pyro instruction", "no energetic-device, pyro, or deployment instruction"),
    ("no pump performance claim", "no pump performance sizing claim"),
    ("no flight-performance claim", "no flight-performance or flight-readiness claim"),
    ("no stability/performance claim", "no stability/performance or flight-readiness claim"),
    ("no live energy system", "no live-energy assembly instruction"),
    ("no deployment charge or flight recovery instruction", "no deployment-charge or flight-recovery instruction"),
]

ID_REPLACEMENTS = [
    ("_dummy", "_reference_article"),
    ("dummy_", "reference_article_"),
    ("_mock", "_study"),
    ("mock_", "study_"),
    ("propulsion_mock", "propulsion_study"),
    ("electrical_distribution_mock", "electrical_distribution_study"),
    ("common_rail_injection_mock", "common_rail_injection_study"),
    ("turbo_air_exhaust_mock", "turbo_air_exhaust_study"),
    ("small_launch_vehicle_mock_boundary", "small_launch_vehicle_academic_boundary"),
    ("safe_mock_vtol_boundary", "safe_academic_vtol_boundary"),
    ("space_mock_boundary", "space_academic_boundary"),
    ("engine_display_cartridge", "engine_study_cartridge"),
    ("engine_display", "engine_study"),
    ("power_display", "power_study"),
    ("separation_display", "separation_study"),
    ("display_only_flowpath", "study_boundary_flowpath"),
]


def replace_text(text: str) -> str:
    out = text
    for old, new in ID_REPLACEMENTS:
        out = out.replace(old, new)
    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    out = out.replace("_reference structure", "_study")
    out = out.replace("reference structure_boundary", "study_boundary")
    out = out.replace("reference structure_domain", "study_domain")
    out = re.sub(r"\bmock\b", "reference structure", out, flags=re.IGNORECASE)
    out = re.sub(r"\bdummy\b", "reference article", out, flags=re.IGNORECASE)
    return out


def transform(obj: Any) -> Any:
    if isinstance(obj, str):
        return replace_text(obj)
    if isinstance(obj, list):
        return [transform(item) for item in obj]
    if isinstance(obj, dict):
        return {key: transform(value) for key, value in obj.items()}
    return obj


def maybe_rename_pack_file(path: Path) -> Path:
    name = path.name
    new_name = replace_text(name)
    if new_name == name:
        return path
    target = path.with_name(new_name)
    if target.exists():
        return path
    path.rename(target)
    return target


def update_json(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    data = transform(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_text(path: Path) -> None:
    if not path.exists():
        return
    path.write_text(replace_text(path.read_text(encoding="utf-8")), encoding="utf-8")


def main() -> int:
    updated = 0
    for path in JSON_PATHS:
        if path.exists():
            update_json(path)
            updated += 1
    for path in sorted((REPO / "20_dataset" / "packs").rglob("*.json")):
        maybe_rename_pack_file(path)
    for path in TEXT_PATHS:
        update_text(path)
    print(f"sanitized json files: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
