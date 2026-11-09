"""N3: check N* where it matters, on real generators: choose n so that N/N* = 0.25, 0.5, 1, 2, 4 for a fixed N,
generate many independent samples (different seeds) and compare the rejection rate of the exact binomial test with
its exact power.

Usage: python3 scripts/threshold_check.py <source-id>   -> results/<source-id>/threshold_check.csv
Needs gcc (glibc rand() % n, w = 31) and Rscript (sample() with Rounding, w = 32).
"""
import csv, os, shutil, subprocess, sys, tempfile
import numpy as np
from scipy.stats import binom, binomtest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import heavy_mask, heavy_probabilities, n_star  # noqa: E402
from src.simulation.power import binomtest_reject_set  # noqa: E402

sid = sys.argv[1]
N, REPS, ALPHA = 10_000, 200, 0.05
FACTORS = (0.25, 0.5, 1, 2, 4)
tmp = tempfile.mkdtemp()


def pick_n(w, target, lo, hi):
    """An n in [lo, hi) whose N* is within 2% of target (deterministic scan)."""
    best = None
    for n in range(lo, hi, max(1, (hi - lo) // 200000)):
        if 2**w % n == 0:
            continue
        ns = n_star(n, w)
        if abs(ns / target - 1) < 0.02:
            return n
        if best is None or abs(ns / target - 1) < abs(n_star(best, w) / target - 1):
            best = n
    return best


def c_samples(n):
    out = []
    for s in range(1, REPS + 1):
        o = subprocess.run([f"{tmp}/rand_mod", str(n), str(N), str(s)], capture_output=True, text=True).stdout
        out.append(np.array([int(v) for v in o.split()], dtype=np.int64))
    return out


def r_samples(n):
    code = (f'suppressWarnings(RNGversion("3.5.0")); RNGkind(sample.kind="Rounding"); '
            f'for (s in 1:{REPS}) {{ set.seed(s); cat(sample.int({n}, {N}, replace=TRUE) - 1, sep="\\n"); cat("\\n") }}')
    o = subprocess.run(["Rscript", "-e", code], capture_output=True, text=True).stdout.split()
    v = np.array([int(float(x)) for x in o], dtype=np.int64)
    return [v[i * N:(i + 1) * N] for i in range(REPS)]


CASES = []
if shutil.which("gcc"):
    subprocess.run(["gcc", "-O2", "-o", f"{tmp}/rand_mod", "src/languages/c/rand_mod.c"], check=True)
    CASES.append(("C rand() % n (glibc)", 31, "mod", c_samples))
if shutil.which("Rscript"):
    CASES.append(("R sample(), Rounding", 32, "mult", r_samples))
rows = []
for name, w, meth, gen in CASES:
    for f in FACTORS:
        target = N / f
        # N* ~ 7.85*4^w/(r(n-r)): search n around the value that gives r(n-r) ~ 7.85*4^w/target with r ~ n/2
        guess = int(2 * np.sqrt(7.85 * 4.0**w / target))
        n = pick_n(w, target, max(3, int(guess * 0.6)), min(2**w - 1, int(guess * 3)))
        p0, p1 = heavy_probabilities(n, w)
        rs = binomtest_reject_set(N, p0, ALPHA)
        exact = float(binom.pmf(np.arange(N + 1), N, p1)[rs].sum())
        ys = gen(n)
        rej = sum(binomtest(int(heavy_mask(y, n, w, meth).sum()), N, p0).pvalue <= ALPHA for y in ys)
        rate = rej / len(ys)
        se = np.sqrt(exact * (1 - exact) / len(ys))
        rows.append({"function": name, "w": w, "n": n, "N": N, "N_over_Nstar": round(N / n_star(n, w), 3),
                     "exact_power": round(exact, 3), "rejection_rate": rate, "reps": len(ys),
                     "z": round((rate - exact) / se, 2) if se > 0 else ""})
        print(rows[-1], flush=True)
os.makedirs(f"results/{sid}", exist_ok=True)
with open(f"results/{sid}/threshold_check.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader()
    wr.writerows(rows)
print("->", f"results/{sid}/threshold_check.csv")
