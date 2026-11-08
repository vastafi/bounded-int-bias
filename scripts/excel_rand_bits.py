"""E5c: resolution of Excel's RAND() from a workbook saved by Excel (exact double values).

Usage: python3 scripts/excel_rand_bits.py <E5_template saved by Excel>.xlsx <source-id>
Reads column C (RAND()) of sheet E5 as stored by Excel, i.e. the exact doubles, and writes
results/<source-id>/excel-sample/excel_rand_exact_N<N>.txt (repr of every value, 17 significant digits)
results/<source-id>/excel-sample/rand_bits.txt          (distribution of the fixed-point bits)

For u = m / 2^d with m odd, d is the number of fixed-point bits u actually uses. A generator returning
k / 2^B with k uniform gives P(d = B - j) = 2^-(j+1): half the values use all B bits, a quarter B - 1, and so on.
Note: do not test this inside Excel with "=": Excel compares with about 15 significant digits.
"""
import os, sys
from fractions import Fraction
from collections import Counter
import openpyxl

path, sid = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
us = [r[2] for r in wb["E5"].iter_rows(min_row=2, values_only=True) if isinstance(r[2], float)]
if not us:
    sys.exit("no cached RAND() values: open the workbook in Excel and save it as .xlsx first")
d = Counter(Fraction(u).denominator.bit_length() - 1 for u in us)
B = max(d)
out = os.path.join("results", sid, "excel-sample")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, f"excel_rand_exact_N{len(us)}.txt"), "w") as fh:
    fh.write("\n".join(repr(u) for u in us) + "\n")
lines = [f"{len(us)} RAND() values from {os.path.basename(path)}; maximum fixed-point bits B = {B}",
         "bits d  observed share  expected share if u = k/2^B, k uniform"]
for j in range(0, 10):
    lines.append(f"{B - j:6d}  {d.get(B - j, 0) / len(us):14.5f}  {2.0 ** -(j + 1):14.5f}")
lines.append(f"share that are multiples of 2^-48: {sum(v for k, v in d.items() if k <= 48) / len(us):.5f} "
             f"(expected {2.0 ** -(B - 48):.5f})")
open(os.path.join(out, "rand_bits.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("->", out)
