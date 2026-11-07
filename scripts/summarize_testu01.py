"""Summarise TestU01 outputs: results/<source-id>/testu01/*.txt -> testu01_summary.csv
Usage: python scripts/summarize_testu01.py <source-id>"""
import csv, glob, os, re, sys

sid = sys.argv[1]
rows = []
for f in sorted(glob.glob(f"results/{sid}/testu01/*_*.txt")):
    gen, battery = os.path.basename(f)[:-4].rsplit("_", 1)
    text = open(f, errors="replace").read()
    block = text.split("Summary results of", 1)[-1] if "Summary results of" in text else ""
    if "All tests were passed" in block:
        failed = []
    else:
        # failing lines look like: "  1  BirthdaySpacings   eps" or "  6  MaxOft   1.0e-12"
        failed = [" ".join(l.split()[1:]) for l in block.splitlines()
                  if re.match(r"^\s*\d+\s+\S+.*(eps|\d\.\d+e-\d+|1 - )", l)]
    m = re.search(r"Number of statistics:\s+(\d+)", block)
    rows.append({"generator": gen, "battery": battery, "statistics": m.group(1) if m else "",
                 "complete": bool(block), "n_failed": len(failed), "failed_tests": "; ".join(failed)})
out = f"results/{sid}/testu01/testu01_summary.csv"
with open(out, "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
    wr.writeheader(); wr.writerows(rows)
for r in rows:
    print(r)
print("->", out)
