"""E5c: estimate the resolution (bits) of a U(0,1) generator from decimal text values.

Usage: python3 scripts/rand_resolution.py results/<source-id>/excel-sample/excel_rand_N100000.txt
For each k, reports the share of values u for which u*2^k is an integer within the rounding error of the text.
A generator with k bits gives share 1.0 from k on. Text with ~15 significant digits resolves k up to about 45.
"""
import sys
from decimal import Decimal

vals = [Decimal(l.strip()) for l in open(sys.argv[1]) if l.strip()]
digits = max(len(str(v).split(".")[1].rstrip("0") or "0") for v in vals)
sig = max(len(str(v).replace("0.", "", 1).lstrip("0").replace(".", "")) for v in vals)
print(f"{len(vals)} values; at most {digits} decimals, {sig} significant digits in the text")
print(f"distinct values: {len(set(vals))}")
for k in (15, 16, 24, 31, 32, 36, 40, 44, 48, 52, 53):
    ok = 0; tol_k = None
    for v in vals:
        e = Decimal(10) ** -(len(str(v).split(".")[1]) if "." in str(v) else 0)   # last-digit unit
        x = v * (2 ** k)
        tol = e * (2 ** k)          # rounding of the text can move x by up to this much
        ok += abs(x - x.to_integral_value()) <= tol / 2 + Decimal("1e-30")
        tol_k = tol
    info = "  (not resolvable: text rounding exceeds 2^-k)" if tol_k is not None and tol_k >= Decimal("0.5") else ""
    print(f"k = {k:2d}: share of values on the 2^-{k} grid = {ok/len(vals):.4f}{info}")
