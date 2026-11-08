"""Check that the repository holds every expected result file, with the expected size, and nothing stray.

Usage (from the repository root): python3 scripts/check_repo.py
Prints OK / MISSING / CHECK lines and a final count.
"""
import glob, json, os, subprocess

problems = 0


def say(status, msg):
    global problems
    problems += status != "OK"
    print(f"{status:8s} {msg}")


def lines(path):
    with open(path, errors="replace") as fh:
        return sum(1 for l in fh if l.strip())


# 1. sources: each needs environment.json and summary.csv; samples have the expected number of values
for sid in ("linux-cloud", "mac-va", "windows-va", "excel-mac-va", "excel-win-va"):
    root = f"results/{sid}"
    if not os.path.isdir(root):
        say("MISSING", f"{root}/")
        continue
    for f in ("environment.json", "summary.csv"):
        p = os.path.join(root, f)
        if not os.path.exists(p):
            say("MISSING", p)
        elif f.endswith(".json"):
            try:
                json.load(open(p))
                say("OK", p)
            except ValueError as e:
                say("CHECK", f"{p}: not valid JSON ({e})")
        else:
            say("OK", f"{p}: {lines(p) - 1} rows")
    for p in sorted(glob.glob(f"{root}/*-sample/*.txt")):
        if any(k in p for k in ("rand_bits", "rand_max", "version", "library")):
            continue
        n = lines(p)
        say("OK" if n in (20, 100000) else "CHECK", f"{p}: {n} values")

# 2. Excel extras
for sid in ("excel-mac-va", "excel-win-va"):
    for f in ("rand_bits.txt", "excel_rand_exact_N100000.txt"):
        p = f"results/{sid}/excel-sample/{f}"
        say("OK" if os.path.exists(p) else "MISSING", p)

# 3. other results
for p in ("results/linux-cloud/power/power.csv", "results/linux-cloud/practical/raffle.csv",
          "results/mac-va/testu01/testu01_summary.csv", "figures/fig1_power.pdf", "figures/fig2_nstar_map.pdf",
          "src/languages/excel/E5_template.xlsx"):
    say("OK" if os.path.exists(p) else "MISSING", p)
p = "results/mac-va/testu01/testu01_summary.csv"
if os.path.exists(p):
    gens = {l.split(",")[0] for l in open(p).read().splitlines()[1:]}
    want = {"raw", "rejection", "mult", "mod", "rejection_d", "mult_d", "mod_d", "mult53_d", "mod53_d"}
    say("OK" if want <= gens else "CHECK", f"TestU01 generators: {len(gens & want)} of 9" +
        ("" if want <= gens else f", missing {sorted(want - gens)}"))

# 4. stray files that should not be committed
tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
for t in tracked:
    stray = (t.endswith(".xlsx") and t != "src/languages/excel/E5_template.xlsx") or \
            (t.endswith(".csv") and not t.startswith("results/")) or t.startswith(("build/", ".idea/"))
    if stray:
        say("CHECK", f"tracked file that should not be in git: {t}")
out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
say("OK" if not out else "CHECK", "git: everything committed" if not out else "git: uncommitted changes:\n" + out)
print(f"\n{problems} problem(s)")
