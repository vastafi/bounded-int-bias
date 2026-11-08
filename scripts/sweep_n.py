"""M6: sweep over the interval size n on one machine (C rand() % n with glibc, R sample() Rounding / Rejection,
Python int(random()*n) and randrange). N = 100,000 values per n, seed 2026.

Usage: python3 scripts/sweep_n.py <source-id>     -> results/<source-id>/sweep_n.csv
Needs gcc and Rscript on the PATH (skips what is missing). For each sample: exact two-sided binomial test of the
heavy count for the function's own (w, method), N*, and whether N >= N* (bias predicted detectable).
"""
import csv, os, shutil, subprocess, sys, tempfile
import numpy as np
from scipy.stats import binomtest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import heavy_mask, heavy_probabilities, n_star  # noqa: E402

sid = sys.argv[1]
N, SEED = 100_000, 2026
NS = [10**k for k in range(2, 10)] + [3 * 2**29]
tmp = tempfile.mkdtemp()
rows = []

if shutil.which("gcc"):
    subprocess.run(["gcc", "-O2", "-o", f"{tmp}/rand_mod", "src/languages/c/rand_mod.c"], check=True)
    rm = subprocess.run([f"{tmp}/rand_mod", "10", "1", "1"], capture_output=True, text=True)


def c_rand(n):
    out = subprocess.run([f"{tmp}/rand_mod", str(n), str(N), str(SEED)], capture_output=True, text=True).stdout
    return np.array([int(v) for v in out.split()], dtype=np.int64)


def r_sample(n, kind):
    code = (f'suppressWarnings(RNGversion("3.5.0")); RNGkind(sample.kind="{kind}"); set.seed({SEED}); '
            f'cat(sample.int({n}, {N}, replace=TRUE) - 1, sep="\\n")')
    out = subprocess.run(["Rscript", "-e", code], capture_output=True, text=True).stdout
    return np.array([int(float(v)) for v in out.split()], dtype=np.int64)


def py_intrandom(n):
    import random
    g = random.Random(SEED)
    return np.array([int(g.random() * n) for _ in range(N)], dtype=np.int64)


def py_randrange(n):
    import random
    g = random.Random(SEED)
    return np.array([g.randrange(n) for _ in range(N)], dtype=np.int64)


FUNCS = [("C rand() % n (glibc)", "mod", 31, c_rand, "gcc"),
         ("R sample(), Rounding", "mult", 32, lambda n: r_sample(n, "Rounding"), "Rscript"),
         ("R sample(), Rejection (control)", "mult", 32, lambda n: r_sample(n, "Rejection"), "Rscript"),
         ("Python int(random()*n)", "mult", 53, py_intrandom, None),
         ("Python randrange (control)", "mult", 32, py_randrange, None)]
for name, meth, w, gen, tool in FUNCS:
    if tool and not shutil.which(tool):
        print(f"{tool} not found: skipped {name}")
        continue
    for n in NS:
        if 2**w % n == 0 or n >= 2**w:
            continue
        y = gen(n)
        assert len(y) == N and y.min() >= 0 and y.max() < n, (name, n)
        p0, _ = heavy_probabilities(n, w)
        k = int(heavy_mask(y, n, w, meth).sum())
        p = binomtest(k, N, p0).pvalue
        ns = n_star(n, w)
        rows.append({"function": name, "n": n, "w": w, "method": meth, "N": N, "Nstar": f"{ns:.3g}",
                     "predicted_detectable": (ns <= N) and "control" not in name, "p_heavy": f"{p:.3g}"})
        print(f"{name:32s} n={n:<11d} N*={ns:9.3g} p={p:.3g}")
# expected power of the two-sided test at this N (normal approximation) and Holm over the whole sweep
from scipy.stats import norm
za, zb = norm.ppf(0.975), norm.ppf(0.8)
for r in rows:
    ratio = N / float(r["Nstar"])
    r["expected_power"] = "0.05" if "control" in r["function"] else f"{norm.cdf((za + zb) * ratio**0.5 - za):.3g}"
order = sorted(range(len(rows)), key=lambda i: float(rows[i]["p_heavy"]))
run = 0.0
for rank, i in enumerate(order):
    run = max(run, min(1.0, (len(rows) - rank) * float(rows[i]["p_heavy"])))
    rows[i]["holm_reject"] = run < 0.05
agree = sum(r["holm_reject"] == r["predicted_detectable"] for r in rows)
print(f"{len(rows)} tests; Holm rejects {sum(r['holm_reject'] for r in rows)}; decision = prediction (N >= N*) in "
      f"{agree} of {len(rows)}")
os.makedirs(f"results/{sid}", exist_ok=True)
with open(f"results/{sid}/sweep_n.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader()
    wr.writerows(rows)
print("->", f"results/{sid}/sweep_n.csv")
