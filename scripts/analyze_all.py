"""Analyse every raw sample of one source and write results/<source-id>/summary.csv.

Usage: python scripts/analyze_all.py <source-id>

Each file is tested against the bias structure of the idiom it comes from (method, w = bits of randomness).
Unbiased functions are tested against the same structure as their biased counterpart (controls).
"""
import csv, glob, gzip, os, re, sys
import numpy as np
from scipy.stats import binomtest, chi2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import heavy_probabilities, is_heavy, n_star  # noqa: E402

# prefix of file name -> (method, w, role)
RULES = [
    ("r_Rounding", "mult", 32, "biased (R <= 3.5)"),
    ("r_Rejection", "mult", 32, "control (R >= 3.6)"),
    ("python_intrandom", "mult", 53, "idiom int(random()*n)"),
    ("python_randrange", "mult", 53, "control"),
    ("python_numpy", "mult", 53, "control"),
    ("java_intdouble", "mult", 53, "idiom (long)(nextDouble()*n)"),
    ("java_nextint", "mod", 31, "control"),
    ("js_floorrandom", "mult", 52, "idiom Math.floor(Math.random()*n)"),
    ("js_cryptorandint", "mod", 48, "control"),
    ("c_randmod", "mod", None, "idiom rand() % n"),      # w from rand_max.txt
    ("excel_randbetween", "mult", 32, "RANDBETWEEN (provisional w)"),
    ("excel_intrand", "mult", 32, "INT(RAND()*n) (provisional w)"),
]


def read_values(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return np.array([int(l) for l in fh if l.strip()], dtype=object)


def c_bits(folder):
    f = os.path.join(folder, "rand_max.txt")
    m = re.search(r"RAND_MAX=(\d+)", open(f).read()) if os.path.exists(f) else None
    return (int(m.group(1)) + 1).bit_length() - 1 if m else None


def main():
    sid = sys.argv[1]
    root = os.path.join("results", sid)
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "*", "*.txt*"))):
        name = os.path.basename(path)
        rule = next((r for r in RULES if name.startswith(r[0])), None)
        mn = re.search(r"_n(\d+)_N(\d+)", name)
        if not rule or not mn:
            continue
        prefix, method, w, role = rule
        if w is None:
            w = c_bits(os.path.dirname(path))
        n = int(mn.group(1))
        ys = read_values(path)
        if prefix.startswith("excel") and min(ys) == 1:
            ys = ys - 1
        row = {"source": sid, "file": name, "role": role, "method": method, "w": w, "n": n, "N": len(ys)}
        if 2**w < n:
            row.update({"note": f"truncated range: only 2^{w} possible values, max observed {max(ys)}"})
            rows.append(row)
            continue
        p0, p1 = heavy_probabilities(n, w)
        h = sum(is_heavy(int(y), n, w, method) for y in ys)
        cnt = np.bincount((ys.astype(np.float64) * 10 / n).astype(np.int64), minlength=10)[:10]
        pb = np.diff(np.ceil(np.arange(11) * n / 10)) / n
        x2 = float(((cnt - len(ys) * pb) ** 2 / (len(ys) * pb)).sum())
        row.update({
            "Nstar": f"{n_star(n, w):.3g}",
            "frac_heavy": round(h / len(ys), 5), "p_heavy_uniform": round(p0, 5), "p_heavy_biased": round(p1, 5),
            "p_heavy_test": f"{binomtest(h, len(ys), p0).pvalue:.3g}",
            "p_chi2_B10": f"{chi2.sf(x2, 9):.3g}",
            "note": "N >= N*: a bias of this structure would be detected" if n_star(n, w) <= len(ys) else "N < N*: bias too small for this N",
        })
        rows.append(row)
    out = os.path.join(root, "summary.csv")
    fields = ["source", "file", "role", "method", "w", "n", "N", "Nstar", "frac_heavy", "p_heavy_uniform",
              "p_heavy_biased", "p_heavy_test", "p_chi2_B10", "note"]
    with open(out, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        wr.writerows(rows)
    for r in rows:
        print(f"{r['file'][:42]:42s} {r['role'][:30]:30s} N*={r.get('Nstar','-'):>9} p_heavy={r.get('p_heavy_test','-'):>9} p_chi2={r.get('p_chi2_B10','-'):>8}  {r['note']}")
    print("->", out)


if __name__ == "__main__":
    main()
