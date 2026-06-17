"""
run_full_pipeline.py -- one-process CAD/audit orchestrator
==========================================================

Runs the whole generated-bundle pipeline in a single Python process so
build123d (OCCT) is imported once instead of 5 subprocess cold-starts.
Used by serve.py /audit-bundle to cut a ~30-90s run down sharply.

Steps (identical outputs to the separate scripts):
  build_solid.build → export_print_parts.export_seed → validate_print.validate_seed
  → export_step_assembly.export_seed → assembly_interference_audit (write_report)
  → analysis_estimate.run

Usage:
  python run_full_pipeline.py <seed> --dir <package_dir>   # generated bundle
  python run_full_pipeline.py <seed>                        # a curated seed
"""
from __future__ import annotations

import sys

import build_solid
import export_print_parts
import validate_print
import export_step_assembly
import assembly_interference_audit as interf
import analysis_estimate


def run_pipeline(seed: str, seed_dir: str | None = None) -> dict:
    """전 단계를 한 프로세스에서 순차 실행. 출력 폴더명은 생성물이면 <seed>_generated."""
    out_name = f"{seed}_generated" if seed_dir else seed
    result = {"seed": seed, "out_name": out_name, "steps": [], "ok": True}

    def step(name, fn):
        try:
            rc = fn()
            result["steps"].append({"step": name, "ok": rc in (0, None, True)})
        except Exception as exc:
            result["steps"].append({"step": name, "ok": False, "error": str(exc)[:200]})
            result["ok"] = False
            raise

    step("build_solid", lambda: build_solid.build(seed, seed_dir))
    step("export_print_parts", lambda: export_print_parts.export_seed(seed, seed_dir))
    step("validate_print", lambda: validate_print.validate_seed(out_name, validate_print.DEFAULT_BED))
    step("export_step_assembly", lambda: export_step_assembly.export_seed(seed, False, False, seed_dir))

    def _interf():
        report = interf.audit_seed(out_name)
        interf.write_report(report)
        return 0
    step("interference_audit", _interf)
    step("analysis_estimate", lambda: analysis_estimate.run(out_name))
    return result


def main(argv):
    rest, seed_dir = build_solid.parse_dir_flag(argv[1:])
    args = [a for a in rest if a]
    if not args:
        print("usage: python run_full_pipeline.py <seed> [--dir <package_dir>]")
        return 1
    res = run_pipeline(args[0], seed_dir)
    print(f"[pipeline] {res['out_name']} · {'OK' if res['ok'] else 'FAIL'} · "
          f"steps {sum(1 for s in res['steps'] if s['ok'])}/{len(res['steps'])}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
