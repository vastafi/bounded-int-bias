"""N2: size and power of the scan over (w, method) by simulation.

Usage: python3 scripts/scan_size.py   -> results/linux-cloud/scan_size.csv
Under H0 (exactly uniform integers from NumPy's integers(), PCG64) the scan of scripts/scan_heavy.py with Holm at
alpha = 0.05 should reject with probability <= 0.05; under a biased reduction its power is compared with the power
of the single test that knows (w, method).
"""
import csv, os, sys
import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.scan_heavy import scan  # noqa: E402
from src.theory.bias import heavy_mask, heavy_probabilities, n_star  # noqa: E402

ALPHA, SEED = 0.05, 2026
rng = np.random.default_rng(SEED)


def holm_reject(ps):
    ps = sorted(ps)
    return any(p <= ALPHA / (len(ps) - i) for i, p in enumerate(ps[:1]))   # Holm rejects iff min p <= alpha/m


def biased(n, N, w, meth):
    k = rng.integers(0, 2**w, size=N, dtype=np.uint64)
    if meth == "mod":
        return (k % np.uint64(n)).astype(np.int64)
    return ((k.astype(object) * n) >> w).astype(np.int64) if w > 32 else ((k * np.uint64(n)) >> np.uint64(w)).astype(np.int64)


rows = []
for n, N, reps in ((3 * 2**29, 100_000, 1000), (20_000, 100_000, 1000)):
    rej = sum(holm_reject([t[2] for t in scan(rng.integers(0, n, size=N), n)]) for _ in range(reps))
    m = len(scan(rng.integers(0, n, size=1000), n))
    rows.append({"case": "H0 (uniform)", "n": n, "N": N, "distinct_tests": m, "reps": reps,
                 "scan_reject_rate": rej / reps, "single_test_power": ""})
    print(rows[-1], flush=True)
for n, w, meth in ((3 * 2**29, 32, "mult"), (3 * 2**29, 31, "mod")):
    N = int(round(n_star(n, w)))
    reps = 1000
    p0, _ = heavy_probabilities(n, w)
    rej_scan = rej_one = 0
    for _ in range(reps):
        y = biased(n, N, w, meth)
        rej_scan += holm_reject([t[2] for t in scan(y, n)])
        rej_one += binomtest(int(heavy_mask(y, n, w, meth).sum()), N, p0).pvalue <= ALPHA
    rows.append({"case": f"{meth}, w = {w}, N = N*", "n": n, "N": N, "distinct_tests": len(scan(y, n)), "reps": reps,
                 "scan_reject_rate": rej_scan / reps, "single_test_power": rej_one / reps})
    print(rows[-1], flush=True)
os.makedirs("results/linux-cloud", exist_ok=True)
with open("results/linux-cloud/scan_size.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader()
    wr.writerows(rows)
print("-> results/linux-cloud/scan_size.csv")
