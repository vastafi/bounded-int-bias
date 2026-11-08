"""M5/M6: test every sample against the heavy sets of all plausible word sizes and methods.

Usage: python3 scripts/scan_heavy.py   -> results/scan_heavy.csv
For each distinct sample (byte-identical files from several sources are analysed once), and each candidate
(w, method) with 2^w > n, the exact two-sided binomial test of the heavy count. The family per sample is the set
of candidates; Holm's correction gives the adjusted minimum p, and a second Holm step over all distinct samples
gives p_global_holm. Reported N* is per candidate.
Candidates: w in {15, 31, 32, 48, 52, 53} x {mod, mult}.
"""
import csv, glob, gzip, hashlib, os, re, sys
import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import heavy_mask, heavy_probabilities, n_star  # noqa: E402

WS = (15, 31, 32, 48, 52, 53)


def read(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return np.array([int(l) for l in fh if l.strip()], dtype=np.int64)


seen, rows = {}, []
for path in sorted(glob.glob("results/*/*/*_n*_N*.txt*")):
    m = re.search(r"_n(\d+)_N(\d+)", os.path.basename(path))
    if not m or "rand_" in os.path.basename(path) and "excel_rand" in path:
        continue
    n = int(m.group(1))
    y = read(path)
    h = hashlib.sha256(y.tobytes()).hexdigest()      # same values = same sample, whatever the line endings
    src = path.split(os.sep)[1]
    if h in seen:
        seen[h]["sources"].append(src)
        continue
    if "excel_randbetween" in path and y.min() >= 1 and y.max() <= n:
        y = y - 1 if y.max() == n else y
    if y.min() < 0 or y.max() >= n:
        continue
    func = re.sub(r"_n\d+.*", "", os.path.basename(path))
    tests = []
    for w in WS:
        if 2**w <= n or 2**w % n == 0:
            continue
        for meth in ("mod", "mult"):
            p0, _ = heavy_probabilities(n, w)
            k = int(heavy_mask(y, n, w, meth).sum())
            tests.append((w, meth, binomtest(k, len(y), p0).pvalue, n_star(n, w)))
    ps = sorted(t[2] for t in tests)
    holm = min(min(1.0, (len(ps) - i) * p) for i, p in enumerate(ps)) if ps else None
    best = min(tests, key=lambda t: t[2]) if tests else None
    rec = {"function": func, "n": n, "N": len(y), "sources": [src], "candidates": len(tests),
           "best_w": best[0] if best else "", "best_method": best[1] if best else "",
           "p_min": best[2] if best else "", "p_holm_min": holm if holm is not None else "",
           "Nstar_best": best[3] if best else "",
           "detail": "; ".join(f"w{t[0]}/{t[1]}:p={t[2]:.3g}" for t in tests)}
    seen[h] = rec
    rows.append(rec)
for r in rows:
    r["sources"] = "+".join(r["sources"])
# second level: Holm over the per-sample adjusted minima (family = all distinct samples)
order = sorted(range(len(rows)), key=lambda i: rows[i]["p_holm_min"])
running = 0.0
for rank, i in enumerate(order):
    running = max(running, min(1.0, (len(rows) - rank) * rows[i]["p_holm_min"]))
    rows[i]["p_global_holm"] = running
with open("results/scan_heavy.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader()
    wr.writerows(rows)
for r in rows:
    print(f"{r['function'][:22]:22s} n={r['n']:<10d} {r['sources'][:34]:34s} cand={r['candidates']:2d} "
          f"best=w{r['best_w']}/{r['best_method']:4s} p_min={float(r['p_min']):.3g} p_holm={float(r['p_holm_min']):.3g} "
          f"global={r['p_global_holm']:.3g}")
print(f"{len(rows)} distinct samples; rejected after both corrections (0.05): "
      + ", ".join(f"{r['function']} n={r['n']} [{r['sources']}]" for r in rows if r["p_global_holm"] < 0.05))
print("->", "results/scan_heavy.csv")
