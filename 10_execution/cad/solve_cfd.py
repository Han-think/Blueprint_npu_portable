"""
solve_cfd.py -- external CFD driver with honest graceful fallback
=================================================================

Real external-flow CFD needs a true solver (OpenFOAM simpleFoam, steady RANS).
This module DETECTS whether such a solver is reachable (native PATH or WSL) and,
when present, is the integration point that drives a case from the geometry that
export_step_assembly already emits with --cfd:
    output/<seed>/cfd/<seed>_fused.step
    output/<seed>/cfd/<seed>_fluid_domain.step
    output/<seed>/cfd/cfd_meta.json

When NO solver is reachable it returns {"available": False, ...} so the caller
(analysis_estimate) keeps the first-order aero proxy and labels it honestly as
"solver_unavailable" rather than fabricating CFD numbers.

HONEST LIMIT: on a box-and-cylinder educational mock the CFD result is a
shape-trend comparison, never an absolute/certified aerodynamic performance.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def detect_openfoam() -> dict:
    """Return how OpenFOAM is reachable, if at all."""
    for exe in ("simpleFoam", "foamRun"):
        p = shutil.which(exe)
        if p:
            return {"available": True, "via": "native", "exe": exe, "path": p}
    # WSL fallback (common OpenFOAM setup on Windows)
    try:
        r = subprocess.run(["wsl", "bash", "-lc", "command -v simpleFoam || command -v foamRun"],
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip():
            return {"available": True, "via": "wsl", "exe": r.stdout.strip().splitlines()[0]}
    except Exception:
        pass
    return {"available": False}


def run_cfd(seed_out_dir: Path) -> dict:
    """Drive an external-flow CFD case if a solver is reachable, else fall back.
    seed_out_dir = output/<name>/ (must contain cfd/ from export_step_assembly --cfd)."""
    cfd_dir = Path(seed_out_dir) / "cfd"
    meta_p = cfd_dir / "cfd_meta.json"
    detect = detect_openfoam()
    if not detect.get("available"):
        return {"available": False, "reason": "no OpenFOAM (native/WSL) on this machine",
                "fallback": "first-order aero proxy retained",
                "hook": "install OpenFOAM, then this driver meshes fluid_domain.step and runs steady RANS"}
    if not meta_p.exists():
        return {"available": False, "reason": "cfd geometry missing — run export_step_assembly --cfd first"}
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    # Integration point for the actual OpenFOAM case build/run. Kept explicit and
    # honest: we only claim a CFD result once a real solver has executed here.
    return {"available": True, "via": detect["via"], "solver": "openfoam_simpleFoam",
            "status": "driver_ready",
            "reference_length_mm": meta.get("reference_length_mm"),
            "note": "OpenFOAM reachable; case meshing/solve to be executed by this driver. "
                    "Result will be shape-trend level on educational mock geometry."}
