"""batch_monitor.py — generate_batch.py 진행 모니터 (터미널 / JupyterLab 둘 다 OK)
사용법:
  python batch_monitor.py              # 1회 출력
  python batch_monitor.py --watch      # 30초마다 자동 갱신 (Ctrl+C 종료)
  python batch_monitor.py --watch 10   # 10초마다
JupyterLab 셀:  !python batch_monitor.py
"""
import json, os, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timedelta

CKPT = Path("/workspace/30_model/curation/batch_checkpoint.json")
LOG  = Path("/workspace/gen.log")
TOTAL = 48
SEEDS = ["cubesat","robot_arm","tiltrotor","small_launch_vehicle","long_range_recon_wing","haptic_glove"]
PER_SEED = 8

def read_ckpt():
    try:
        return json.loads(CKPT.read_text())
    except Exception:
        return {"done": 0, "by_seed": {}}

def log_tail(n=15):
    try:
        lines = LOG.read_text(errors="replace").splitlines()
        return lines[-n:]
    except Exception:
        return ["(log not found)"]

def is_alive():
    try:
        r = subprocess.run(["pgrep", "-f", "generate_batch"], capture_output=True)
        return r.returncode == 0
    except Exception:
        return False

def eta_estimate(done):
    if done < 1:
        return None
    try:
        mtime = os.path.getmtime(LOG)
        ctime = os.path.getctime(LOG)
        elapsed = max(mtime - ctime, 1)
        per_item = elapsed / done
        remain = (TOTAL - done) * per_item
        return remain
    except Exception:
        return None

def render():
    ck = read_ckpt()
    done = ck["done"]
    by_seed = ck.get("by_seed", {})
    alive = is_alive()
    pct = done / TOTAL * 100
    remain = eta_estimate(done)

    status = "RUNNING" if alive else "STOPPED"
    eta_str = ""
    if remain is not None:
        h = int(remain // 3600)
        m = int((remain % 3600) // 60)
        finish = datetime.now() + timedelta(seconds=remain)
        eta_str = f"~{h}h {m}m left -> {finish:%m/%d %H:%M}"

    bar_full = int(pct / 100 * 30)
    bar = "#" * bar_full + "-" * (30 - bar_full)

    lines = []
    lines.append(f"{'='*52}")
    lines.append(f"  generate_batch.py monitor")
    lines.append(f"{'='*52}")
    lines.append(f"  status : {status}")
    lines.append(f"  progress: [{bar}] {done}/{TOTAL} ({pct:.0f}%)")
    if eta_str:
        lines.append(f"  ETA     : {eta_str}")
    lines.append(f"{'─'*52}")

    for s in SEEDS:
        n = by_seed.get(s, 0)
        filled = "#" * n + "." * (PER_SEED - n)
        mark = " done" if n >= PER_SEED else ""
        lines.append(f"  {s:.<30s} [{filled}] {n}/{PER_SEED}{mark}")

    lines.append(f"{'─'*52}")
    lines.append(f"  recent log:")
    for line in log_tail(10):
        lines.append(f"    {line}")
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
