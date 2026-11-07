"""Power of the heavy-value test vs. chi-square with B equal classes.

Usage:
  python -m src.simulation.power --out results/<source-id>/power --reps 400 --bins 10 100 1000 10000
"""
import argparse, csv, json, os, sys
import numpy as np
from scipy.stats import norm, chi2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.theory.bias import split, n_star, is_heavy  # noqa: E402

W_BITS = 32
W = 2**W_BITS


def sample(rng, n, N, method):
    k = rng.integers(0, W, size=N, dtype=np.uint64)
    if method == "mod":
        return k % np.uint64(n)
    return (k * np.uint64(n)) >> np.uint64(W_BITS)  # n < 2^32 keeps the product < 2^64


def heavy_mask(y, n, method):
    if method == "mod":
        return y < split(n, W_BITS)[1]
    return np.fromiter((is_heavy(int(v), n, W_BITS, "mult") for v in y), dtype=bool, count=len(y))


def chi2_reject(y, n, N, B, alpha):
    cls = (y.astype(np.float64) * B / n).astype(np.int64)
    cnt = np.bincount(cls, minlength=B)[:B]
    edges = np.ceil(np.arange(B + 1) * n / B)          # exact class sizes
    p = np.diff(edges) / n
    x2 = ((cnt - N * p) ** 2 / (N * p)).sum()
    return x2 > chi2.ppf(1 - alpha, B - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, nargs="+", default=[1610612736, 10**9, 3 * 10**8, 2 * 10**8])
    ap.add_argument("--factors", type=float, nargs="+", default=[0.25, 0.5, 1, 2, 4])
    ap.add_argument("--bins", type=int, nargs="+", default=[1000])
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    zc = norm.ppf(1 - a.alpha / 2)
    rows = []
    for n in a.n:
        q, r = split(n, W_BITS)
        p0 = r / n
        ns = n_star(n, W_BITS, a.alpha)
        for method in ("mult", "mod"):
            for f in a.factors:
                N = max(20, int(f * ns))
                rej_a = 0
                rej_c = {B: 0 for B in a.bins}
                for _ in range(a.reps):
                    y = sample(rng, n, N, method)
                    h = heavy_mask(y, n, method).sum()
                    rej_a += abs((h - N * p0) / np.sqrt(N * p0 * (1 - p0))) > zc
                    for B in a.bins:
                        rej_c[B] += chi2_reject(y, n, N, B, a.alpha)
                row = {"n": n, "method": method, "N_over_Nstar": f, "N": N, "Nstar_formula": round(ns, 1),
                       "power_heavy_test": rej_a / a.reps}
                row.update({f"power_chi2_B{B}": rej_c[B] / a.reps for B in a.bins})
                rows.append(row)
                print(row, flush=True)
    with open(os.path.join(a.out, "power.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    with open(os.path.join(a.out, "params.json"), "w") as fh:
        json.dump(vars(a), fh, indent=2)


if __name__ == "__main__":
    main()
