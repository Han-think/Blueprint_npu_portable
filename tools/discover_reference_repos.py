"""Discover public GitHub repository candidates for seed reference CAD.

This does not download assets. It queries GitHub repository search and prints
repo/license/star metadata so sources can be reviewed before ingestion.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

QUERIES = {
    "inline_6_engine_gasoline": [
        "engine block FreeCAD STEP STL",
        "straight six engine CAD STEP STL",
    ],
    "inline_6_engine_diesel": [
        "diesel engine FreeCAD STEP STL",
        "common rail engine CAD STEP STL",
    ],
    "centrifugal_pump": [
        "centrifugal pump FreeCAD STEP STL",
        "pump impeller volute CAD STEP STL",
    ],
    "hydraulic_manifold": [
        "hydraulic manifold FreeCAD STEP STL",
        "valve manifold CAD STEP STL",
    ],
    "battery_pack_module": [
        "battery pack FreeCAD STEP STL",
        "battery module CAD STEP STL",
    ],
    "liquid_cold_plate": [
        "cold plate FreeCAD STEP STL",
        "liquid cooling plate CAD STEP STL",
    ],
    "cnc_axis_carriage": [
        "linear rail carriage FreeCAD STEP STL",
        "cnc axis ballscrew CAD STEP STL",
    ],
    "gearbox_reducer": [
        "gearbox reducer FreeCAD STEP STL",
        "gear train housing CAD STEP STL",
    ],
    "underwater_sealed_sensor_housing": [
        "underwater housing FreeCAD STEP STL",
        "o-ring sensor housing CAD STEP STL",
    ],
    "liquid_rocket_engine_academic": [
        "liquid rocket engine academic CAD cutaway",
        "liquid rocket engine regenerative cooling academic diagram",
    ],
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "BlueprintReferenceDiscovery/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    for seed, queries in QUERIES.items():
        print(f"\n## {seed}")
        seen = set()
        for query in queries:
            url = (
                "https://api.github.com/search/repositories?q="
                + urllib.parse.quote(query)
                + "&sort=stars&order=desc&per_page=5"
            )
            try:
                data = fetch_json(url)
            except Exception as exc:
                print(f"[warn] {query}: {type(exc).__name__}: {exc}")
                continue
            print(f"# query: {query}")
            for item in data.get("items", []):
                full_name = item.get("full_name")
                if full_name in seen:
                    continue
                seen.add(full_name)
                license_obj = item.get("license") or {}
                print(
                    f"- {full_name} | stars={item.get('stargazers_count')} | "
                    f"license={license_obj.get('spdx_id') or license_obj.get('name') or 'unknown'} | "
                    f"{item.get('html_url')}"
                )
            time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
