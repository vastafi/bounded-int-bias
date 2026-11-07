"""Integers 0..n-1 from Python, three ways.
  randrange    : random.randrange(n)            (rejection on getrandbits: unbiased)
  intrandom    : int(random.random() * n)       (mult, w = 53)
  numpy        : numpy.random.default_rng().integers(n)   (unbiased; skipped if numpy is missing)
Usage: python src/languages/python/sample_python.py <n> <N> <seed> <outdir>
"""
import os, random, sys

n, N, seed, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
os.makedirs(out, exist_ok=True)
tag = f"n{n}_N{N}_seed{seed}"


def dump(name, values):
    with open(os.path.join(out, f"python_{name}_{tag}.txt"), "w") as fh:
        fh.write("\n".join(map(str, values)) + "\n")


rng = random.Random(seed)
dump("randrange", [rng.randrange(n) for _ in range(N)])
rng = random.Random(seed)
dump("intrandom", [int(rng.random() * n) for _ in range(N)])
try:
    import numpy as np
    dump("numpy", np.random.default_rng(seed).integers(0, n, size=N).tolist())
except ImportError:
    print("numpy not installed: numpy variant skipped", file=sys.stderr)
with open(os.path.join(out, "version.txt"), "w") as fh:
    fh.write(sys.version + "\n")
