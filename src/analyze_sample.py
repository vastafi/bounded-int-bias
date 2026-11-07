"""Analyse a file of integers (one per line, values 0..n-1) produced by ANY source:
R, Python, C/C++ (Linux, Mac, Windows), Java, JavaScript, Excel export.

Reports the heavy-value test (p-value) at several prefix lengths and chi-square with B classes.
Usage:
  python src/analyze_sample.py FILE --n 1610612736 --method mult --w 32 [--bins 1000] [--json out.json]
If the values are 1..n (Excel RANDBETWEEN(1,n)), pass --offset 1.
"""
import argparse, gzip, json, os, sys
import numpy as np
from scipy.stats import binomtest, chi2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import heavy_probabilities, is_heavy, n_star  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--method", choices=["mult", "mod"], required=True,
                    help="bias structure to test against")
    ap.add_argument("--w", type=int, default=32, help="bits of the underlying random word")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--bins", type=int, default=1000)
    ap.add_argument("--json")
    a = ap.parse_args()

    opener = gzip.open if a.file.endswith('.gz') else open
    with opener(a.file, 'rt') as fh:
        ys = [int(l) - a.offset for l in fh if l.strip()]
    if min(ys) < 0 or max(ys) >= a.n:
        sys.exit("values outside 0..n-1; check --n / --offset")
    p0, p1 = heavy_probabilities(a.n, a.w)
    heavy = np.array([is_heavy(y, a.n, a.w, a.method) for y in ys])
    out = {"file": os.path.basename(a.file), "n": a.n, "w": a.w, "method": a.method,
           "N_total": len(ys), "p_heavy_uniform": p0, "p_heavy_biased": p1,
           "Nstar_formula": n_star(a.n, a.w), "prefix_tests": []}
    N = 100
    while N <= len(ys):
        h = int(heavy[:N].sum())
        out["prefix_tests"].append({"N": N, "frac_heavy": h / N, "p_value": binomtest(h, N, p0).pvalue})
        N *= 10
    y = np.array(ys, dtype=np.float64)
    cnt = np.bincount((y * a.bins / a.n).astype(np.int64), minlength=a.bins)[: a.bins]
    p = np.diff(np.ceil(np.arange(a.bins + 1) * a.n / a.bins)) / a.n
    x2 = float(((cnt - len(ys) * p) ** 2 / (len(ys) * p)).sum())
    out["chi2"] = {"bins": a.bins, "stat": x2, "p_value": float(chi2.sf(x2, a.bins - 1))}
    print(json.dumps(out, indent=2))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
