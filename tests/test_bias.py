"""Exhaustive checks of the theory on small word sizes (run: python -m pytest tests)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import is_heavy, heavy_probabilities, bias_gap, split


def counts(n, w, method):
    W = 2**w
    c = [0] * n
    for k in range(W):
        y = (k % n) if method == "mod" else (n * k) // W
        c[y] += 1
    return c


def test_heavy_classification_exhaustive():
    for w in (6, 8, 10):
        for n in range(2, 2**w):
            q, r = split(n, w)
            for method in ("mod", "mult"):
                c = counts(n, w, method)
                for y in range(n):
                    assert (c[y] == q + 1) == is_heavy(y, n, w, method)
                assert sum(v == q + 1 for v in c) == r


def test_gap_formula():
    for w in (8, 10):
        for n in range(2, 2**w):
            p0, p1 = heavy_probabilities(n, w)
            assert abs((p1 - p0) - bias_gap(n, w)) < 1e-15


def test_heavy_mask_closed_form():
    import numpy as np
    from src.theory.bias import heavy_mask, is_heavy
    for w in (6, 8, 10):
        for n in range(2, 2**w):
            if 2**w % n == 0:
                continue
            ys = np.arange(n)
            for m in ("mod", "mult"):
                assert list(heavy_mask(ys, n, w, m)) == [is_heavy(int(y), n, w, m) for y in ys]
