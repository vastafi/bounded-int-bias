"""Accuracy of N* against exact binomial power (numerical check of the approximation (3)).

Usage: python3 src/theory/nstar_accuracy.py  -> results/linux-cloud/nstar_accuracy.csv
Test: H ~ Bin(N, p) = number of heavy values; the exact two-sided binomial test used in the audit (scipy
binomtest, 'minlike' p-value) for N <= 2*10^5, and the equal-tailed exact test above that (the two coincide for
large N). Exact power under p1. Because exact binomial power is not monotone in N (sawtooth), N_exact is defined as
the smallest N on a fine grid (0.25 N* to 4 N*) beyond which the power stays >= 0.8.
Also reports N_norm = (z_a*s0 + z_b*s1)^2 / delta^2 (normal approximation without s1 = s0) and the bound
|s1^2/s0^2 - 1| <= n / 2^w.
"""
import csv, math, os, sys
import numpy as np
from scipy.stats import binom, norm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.theory.bias import heavy_probabilities, n_star  # noqa: E402

ALPHA, POWER = 0.05, 0.80
ZA, ZB = norm.ppf(1 - ALPHA / 2), norm.ppf(POWER)


def exact_power(N, p0, p1):
    if N <= 200_000:
        from src.simulation.power import binomtest_reject_set
        rs = binomtest_reject_set(int(N), p0, ALPHA)
        h = np.arange(int(N) + 1)
        return float(binom.pmf(h, N, p1)[rs].sum()), float(binom.pmf(h, N, p0)[rs].sum())
    lo = binom.ppf(ALPHA / 2, N, p0)          # smallest c with P0(H <= c) >= a/2
    if binom.cdf(lo, N, p0) > ALPHA / 2:
        lo -= 1
    hi = binom.isf(ALPHA / 2, N, p0) + 1      # smallest c with P0(H >= c) <= a/2
    size = binom.cdf(lo, N, p0) + binom.sf(hi - 1, N, p0)
    pw = binom.cdf(lo, N, p1) + binom.sf(hi - 1, N, p1)
    return pw, size


def n_exact(p0, p1, guess):
    Ns = np.unique(np.round(np.geomspace(max(5, guess * 0.25), guess * 4, 800)).astype(np.int64))
    pws = np.array([exact_power(int(N), p0, p1)[0] for N in Ns])
    bad = np.nonzero(pws < POWER)[0]
    if len(bad) == 0:
        return int(Ns[0])
    return int(Ns[bad[-1] + 1]) if bad[-1] + 1 < len(Ns) else None


CASES = [(w, n) for w in (8, 12, 16, 20) for n in
         sorted({3, 5, 7, 2**w // 1000 + 1, 2**w // 100 + 3, 2**w // 10 + 1, 2**w // 3, (2**w * 3) // 4 + 1, 2**w - 3})
         if 2 < n < 2**w and 2**w % n] + [(15, 20000), (15, 1000), (31, 20000), (32, 3 * 2**29), (31, 3 * 2**29)]
rows = []
for w, n in CASES:
    p0, p1 = heavy_probabilities(n, w)
    d = p1 - p0
    s0, s1 = math.sqrt(p0 * (1 - p0)), math.sqrt(p1 * (1 - p1))
    ns = n_star(n, w, ALPHA, POWER)
    nn = (ZA * s0 + ZB * s1) ** 2 / d ** 2
    if ns > 1e12:
        rows.append(dict(w=w, n=n, n_over_2w=n / 2**w, Nstar=ns, N_norm=nn, N_exact="", power_at_Nstar="",
                         size_at_Nstar="", ratio_exact_over_Nstar="", var_ratio_minus1=s1**2 / s0**2 - 1))
        continue
    pw, sz = exact_power(int(round(ns)), p0, p1)
    ne = n_exact(p0, p1, ns)
    rows.append(dict(w=w, n=n, n_over_2w=n / 2**w, Nstar=ns, N_norm=nn, N_exact=ne, power_at_Nstar=pw,
                     size_at_Nstar=sz, ratio_exact_over_Nstar=ne / ns if ne else "", var_ratio_minus1=s1**2 / s0**2 - 1))
out = "results/linux-cloud/nstar_accuracy.csv"
with open(out, "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader()
    wr.writerows(rows)
for r in rows:
    f = lambda x, s=".4g": format(x, s) if x != "" else "-"
    print(f"w={r['w']:2d} n={r['n']:>11d} n/2^w={r['n_over_2w']:.4f} N*={f(r['Nstar'])} N_exact={f(r['N_exact'], 'd') if r['N_exact'] else '-'}"
          f" ratio={f(r['ratio_exact_over_Nstar'])} power@N*={f(r['power_at_Nstar'])} size={f(r['size_at_Nstar'])}"
          f" s1^2/s0^2-1={r['var_ratio_minus1']:+.3g}")
print("->", out)
