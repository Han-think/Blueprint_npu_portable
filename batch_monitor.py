"""batch_monitor.py — generate_batch.py 진행 모니터
사용법:
  python batch_monitor.py              # 1회 출력
  python batch_monitor.py --watch      # 30초마다 자동 갱신 (Ctrl+C 종료)
  python batch_monitor.py --watch 10   # 10초마다
"""
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timedelta

REPO = Path(__file__).resolve().parent
CKPT = REPO / "30_model" / "curation" / "batch_checkpoint.json"
CURATION_LOG = REPO / "30_model" / "curation" / "curation_log.jsonl"
SEEDS_DIR = REPO / "20_dataset" / "seeds_generated"
LOG = Path("/workspace/gen.log")
SEEDS = ["cubesat", "robot_arm", "tiltrotor", "small_launch_vehicle", "long_range_recon_wing", "haptic_glove"]
TOTAL = 300
PER_SEED = 50


def read_ckpt():
    try:
        return json.loads(CKPT.read_text(encoding="utf-8"))
    except Exception:
        return {"done": 0, "by_seed": {}}


def read_curation_stats():
    stats = {"keep": 0, "reject": 0, "hold": 0, "by_seed": {}, "fos_list": []}
    for s in SEEDS:
        stats["by_seed"][s] = {"keep": 0, "reject": 0, "hold": 0, "fos": []}
    try:
        for line in CURATION_LOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            d = row.get("decision", "")
            seed = row.get("seed", "")
            sc = row.get("engineering_scorecard", {})
            if d in ("keep", "reject", "hold"):
                stats[d] += 1
            if seed in stats["by_seed"] and d in ("keep", "reject", "hold"):
                stats["by_seed"][seed][d] += 1
            fos = (sc or {}).get("sizing_fos")
            if isinstance(fos, (int, float)):
                stats["fos_list"].append(fos)
                stats["by_seed"].get(seed, {}).setdefault("fos", []).append(fos)
    except Exception:
        pass
    return stats


def count_files(seed):
    d = SEEDS_DIR / seed
    if not d.exists():
        return 0
    return len([x for x in d.iterdir() if x.is_dir()])


def is_alive():
    try:
        r = subprocess.run(["pgrep", "-f", "generate_batch"], capture_output=True)
        return r.returncode == 0
    except Exception:
        return False


def bar(current, total, width=20):
    if total == 0:
        return "[" + "." * width + "]"
    filled = min(int(current / total * width), width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def avg(lst):
    return sum(lst) / len(lst) if lst else 0


def render():
    ck = read_ckpt()
    cs = read_curation_stats()
    done = ck["done"]
    pct = done / TOTAL * 100 if TOTAL > 0 else 0
    alive = is_alive()
    status = "\033[92mRUNNING\033[0m" if alive else "\033[91mSTOPPED\033[0m"

    total_files = sum(count_files(s) for s in SEEDS)
    total_keep = cs["keep"]
    total_reject = cs["reject"]
    total_hold = cs["hold"]
    total_curated = total_keep + total_reject + total_hold
    keep_rate = total_keep / total_curated * 100 if total_curated > 0 else 0
    avg_fos = avg(cs["fos_list"])

    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("  BATCH GENERATION MONITOR                        " + status)
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Total:   {bar(done, TOTAL, 35)} {done}/{TOTAL} ({pct:.1f}%)")
    lines.append(f"  Files: {total_files}   Curated: {total_curated}   "
                 f"Keep: \033[92m{total_keep}\033[0m  Reject: \033[91m{total_reject}\033[0m  "
                 f"Hold: \033[93m{total_hold}\033[0m  (Keep rate: {keep_rate:.0f}%)")
    if avg_fos > 0:
        lines.append(f"  Avg FoS: {avg_fos:.1f}")
    lines.append("")
    lines.append("-" * 70)
    lines.append(f"  {'Seed':<26s} {'Progress':<28s} {'Disk':>4s}  {'K':>2s}/{'R':>2s}/{'H':>2s}  {'AvgFoS':>6s}")
    lines.append("-" * 70)

    for s in SEEDS:
        seed_ckpt = ck.get("by_seed", {}).get(s, 0)
        files = count_files(s)
        sd = cs["by_seed"].get(s, {})
        k = sd.get("keep", 0)
        r = sd.get("reject", 0)
        h = sd.get("hold", 0)
        seed_fos = avg(sd.get("fos", []))
        fos_str = f"{seed_fos:.1f}" if seed_fos > 0 else "  -"
        seed_pct = seed_ckpt / PER_SEED * 100 if PER_SEED > 0 else 0

        name = s[:24]
        lines.append(
            f"  {name:<26s} {bar(seed_ckpt, PER_SEED, 15)} "
            f"{seed_ckpt:>2d}/{PER_SEED:<2d} ({seed_pct:>4.0f}%)  "
            f"{files:>4d}  {k:>2d}/{r:>2d}/{h:>2d}  {fos_str:>6s}"
        )

    lines.append("-" * 70)

    # ETA
    if done > 1:
        try:
            log_path = LOG if LOG.exists() else REPO.parent / "gen.log"
            if log_path.exists():
                mtime = os.path.getmtime(log_path)
                ctime = os.path.getctime(log_path)
                elapsed = max(mtime - ctime, 1)
                per_item = elapsed / done
                remain = (TOTAL - done) * per_item
                h = int(remain // 3600)
                m = int((remain % 3600) // 60)
                finish = datetime.now() + timedelta(seconds=remain)
                lines.append(f"  ETA: ~{h}h {m}m remaining -> finish ~{finish:%H:%M} (local)")
        except Exception:
            pass

    lines.append(f"  Updated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append("")

    print("\n".join(lines))


def main():
    watch = False
    interval = 30
    args = sys.argv[1:]
    if "--watch" in args:
        watch = True
        idx = args.index("--watch")
        if idx + 1 < len(args):
            try:
                interval = int(args[idx + 1])
            except ValueError:
                pass

    if not watch:
        render()
        return

    try:
        while True:
            os.system("clear" if os.name != "nt" else "cls")
            render()
            print(f"  (refreshing every {interval}s — Ctrl+C to stop)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
