"""Exact bias of bounded-integer conversion methods and the detectability threshold.

Source of random words: uniform integers k in [0, 2^w).
Methods that map k to {0, ..., n-1}:
  mult : y = floor(n * k / 2^w)   (R <= 3.5 sample(), INT(RAND()*n), floor(U*n))
  mod  : y = k mod n              (rand() % n)
With q, r = divmod(2^w, n), exactly r values receive q+1 preimages ("heavy"),
the other n-r values receive q preimages.
"""
from math import ceil
from scipy.stats import norm


def split(n: int, w: int):
    """Return (q, r) with 2^w = q*n + r."""
    return divmod(2**w, n)


def is_heavy(y: int, n: int, w: int, method: str) -> bool:
    """True if output value y has q+1 preimages under the given method."""
    W = 2**w
    q, r = divmod(W, n)
    if method == "mod":
        return y < r
    if method == "mult":
        c = (-(-W * (y + 1) // n)) - (-(-W * y // n))  # exact integer ceil difference
        return c == q + 1
    raise ValueError(method)


def heavy_probabilities(n: int, w: int):
    """(p0, p1): probability of a heavy value under exact uniformity and under the biased method."""
    q, r = split(n, w)
    return r / n, r * (q + 1) / 2**w


def bias_gap(n: int, w: int) -> float:
    """p1 - p0 = r(n-r) / (n 2^w); identical for mod and mult."""
    q, r = split(n, w)
    return r * (n - r) / (n * 2**w)


def n_star(n: int, w: int, alpha: float = 0.05, power: float = 0.80) -> float:
    """Approximate sample size for the heavy-value test to reach the given power.

    N* ~ (z_{1-alpha/2} + z_{power})^2 * 4^w / (r (n - r)).
    Status: algebraic derivation + numerical check (see results/); rigorous proof pending.
    """
    q, r = split(n, w)
    if r == 0:
        return float("inf")  # n divides 2^w: no bias
    z = norm.ppf(1 - alpha / 2) + norm.ppf(power)
    return z * z * 4.0**w / (r * (n - r))


def worst_ratio(n: int, w: int) -> float:
    """Ratio of largest to smallest output probability, (q+1)/q, when r > 0."""
    q, r = split(n, w)
    return (q + 1) / q if r else 1.0
