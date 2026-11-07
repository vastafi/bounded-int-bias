"""Write results/<source-id>/environment.json: who ran what, where, with which versions.

Usage: python scripts/record_env.py <source-id> [--note "text"]
Examples of source-id: linux-cloud, mac-va, windows-va, excel-win-va, excel-mac-va
"""
import argparse, datetime, json, os, platform, shutil, subprocess


def ver(cmd):
    if not shutil.which(cmd[0]):
        return None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (r.stdout or r.stderr).strip().splitlines()[0]
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_id")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    env = {
        "source_id": a.source_id,
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "os": platform.platform(),
        "machine": platform.machine(),
        "cpu": platform.processor(),
        "python": platform.python_version(),
        "R": ver(["R", "--version"]),
        "gcc": ver(["gcc", "--version"]),
        "clang": ver(["clang", "--version"]),
        "java": ver(["java", "-version"]),
        "node": ver(["node", "--version"]),
        "note": a.note,
    }
    try:
        import numpy, scipy
        env["numpy"], env["scipy"] = numpy.__version__, scipy.__version__
    except ImportError:
        pass
    d = os.path.join("results", a.source_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "environment.json"), "w") as fh:
        json.dump(env, fh, indent=2)
    print(json.dumps(env, indent=2))


if __name__ == "__main__":
    main()
