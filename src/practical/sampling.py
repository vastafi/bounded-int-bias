"""M8: effect on a simulation output. Simple random sampling without replacement of k records out of m by a
partial Fisher-Yates shuffle, j = t + rand() % (m - t), as hand-written code often does.

Population: x_i = i / (m - 1), i = 0..m-1 (records in their stored order, e.g. by date); the target is the
population mean 0.5. Estimator: the sample mean. R replications, each from its own seed (MSVC states: SplitMix64 hash of the replicate index).
Generators: Windows rand() (exact MSVC model, 15 bits); a uniform 15-bit word (separates the reduction from the
LCG's own defects); a 31-bit word reduced with % (models glibc rand(), whose
words are treated as uniform here); an unbiased reduction (control).

Usage: python3 src/practical/sampling.py [out_dir]   -> <out_dir>/sampling.csv
"""
import csv, os, sys
import numpy as np

m, k, R, CHUNK = 20_000, 1_000, 4_000, 500
# standard deviation of the mean of a simple random sample without replacement from x_i = i/(m-1)
SRS_SD = float(np.sqrt(np.var(np.arange(m) / (m - 1)) * (m - k) / (k * (m - 1))))


def splitmix64(x):
    """Hash replicate indices into well-separated seeds (consecutive LCG seeds give correlated early outputs)."""
    with np.errstate(over="ignore"):
        z = x + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def run(kind, seed0=2026):
    means = []
    for c0 in range(0, R, CHUNK):
        reps = min(CHUNK, R - c0)
        perm = np.tile(np.arange(m, dtype=np.int32), (reps, 1))
        rows = np.arange(reps)
        state = splitmix64(np.arange(c0, c0 + reps, dtype=np.uint64) + np.uint64(seed0)) & np.uint64(0xFFFFFFFF)
        rng = np.random.default_rng(seed0 + c0)
        for t in range(k):
            span = m - t
            if kind == "msvc15":
                state = (state * np.uint64(214013) + np.uint64(2531011)) & np.uint64(0xFFFFFFFF)
                v = ((state >> np.uint64(16)) & np.uint64(0x7FFF)).astype(np.int64)
                j = t + (v % span)
            elif kind == "mod15":
                v = rng.integers(0, 2**15, size=reps, dtype=np.int64)
                j = t + (v % span)
            elif kind == "mod31":
                v = rng.integers(0, 2**31, size=reps, dtype=np.int64)
                j = t + (v % span)
            else:
                j = t + rng.integers(0, span, size=reps)
            a, b = perm[rows, t].copy(), perm[rows, j].copy()
            perm[rows, t], perm[rows, j] = b, a
        means.append(perm[:, :k].mean(axis=1) / (m - 1))
    x = np.concatenate(means)
    return x.mean(), x.std(ddof=1) / np.sqrt(len(x)), x.std(ddof=1)


out = sys.argv[1] if len(sys.argv) > 1 else "results/linux-cloud/practical"
os.makedirs(out, exist_ok=True)
rows = []
for kind, label in (("msvc15", "Windows rand() % (m - t), 15 bits"),
                    ("mod15", "uniform 15-bit word % (m - t) (reduction only)"), ("mod31", "31-bit word % (m - t)"),
                    ("unbiased", "unbiased reduction (control)")):
    mean, se, sd = run(kind)
    rows.append({"generator": label, "m": m, "k": k, "replications": R, "mean_of_sample_means": f"{mean:.5f}",
                 "bias": f"{mean - 0.5:+.5f}", "mc_se": f"{se:.5f}", "z": f"{(mean - 0.5) / se:+.1f}",
                 "bias_in_sampling_sd": f"{(mean - 0.5) / sd:+.3f}",
                 "bias_in_srs_sd": f"{(mean - 0.5) / SRS_SD:+.3f}"})
    print(rows[-1], flush=True)
with open(os.path.join(out, "sampling.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("->", os.path.join(out, "sampling.csv"))
