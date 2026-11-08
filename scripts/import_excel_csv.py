"""Convert the CSV saved from src/languages/excel/E5_template.xlsx into the three sample files.

Usage: python3 scripts/import_excel_csv.py <path/to/E5.csv> <source-id>      e.g. excel-win-va
Writes results/<source-id>/excel-sample/excel_{randbetween,intrand}_n1610612736_N100000.txt and excel_rand_N100000.txt
Accepts both "," and ";" as separator and a decimal comma (Romanian regional settings).
"""
import csv, os, sys

src, sid = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8-sig", errors="replace").read()
delim = ";" if raw.splitlines()[0].count(";") >= 2 else ","
rows = list(csv.reader(raw.splitlines(), delimiter=delim))
data = [r for r in rows[1:] if len(r) >= 3 and r[0].strip()]
out = os.path.join("results", sid, "excel-sample")
os.makedirs(out, exist_ok=True)


def as_int(x):
    x = x.strip().replace(" ", "").replace(" ", "")
    return int(float(x.replace(",", "."))) if ("," in x or "." in x) else int(x)


files = {"excel_randbetween_n1610612736_N100000.txt": [str(as_int(r[0])) for r in data],
         "excel_intrand_n1610612736_N100000.txt": [str(as_int(r[1])) for r in data],
         "excel_rand_N100000.txt": [r[2].strip().replace(",", ".") for r in data]}
for name, vals in files.items():
    with open(os.path.join(out, name), "w") as fh:
        fh.write("\n".join(vals) + "\n")
    print(f"{name}: {len(vals)} values")
n = len(data)
if n != 100000:
    print(f"warning: expected 100000 rows, found {n}")
print("->", out)
