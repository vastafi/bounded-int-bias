"""E4: compare the raw outputs of two sources that used the same seed.

Usage: python scripts/compare_sources.py <source-a> <source-b>
Writes results/reproducibility_<a>_vs_<b>.csv
"""
import csv, glob, gzip, os, sys


def read(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as fh:
        return [l.strip() for l in fh if l.strip()]


def main():
    a, b = sys.argv[1], sys.argv[2]
    rows = []
    for pa in sorted(glob.glob(f"results/{a}/*/*_seed*.txt*")):
        rel = os.path.relpath(pa, f"results/{a}")
        pb = os.path.join("results", b, rel)
        if not os.path.exists(pb):
            continue
        xa, xb = read(pa), read(pb)
        first = next((i for i, (x, y) in enumerate(zip(xa, xb)) if x != y), None)
        rows.append({"file": rel, "identical": xa == xb, "first_difference_index": "" if first is None else first,
                     f"{a}_first5": " ".join(xa[:5]), f"{b}_first5": " ".join(xb[:5])})
    out = f"results/reproducibility_{a}_vs_{b}.csv"
    with open(out, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    for r in rows:
        print(f"{r['file']:70s} identic={r['identical']}")
    print("->", out)


if __name__ == "__main__":
    main()
