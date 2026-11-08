"""Holm and Benjamini-Hochberg over every p-value of the audit (all sources' summary.csv).

Usage: python3 scripts/multiple_testing.py            -> results/multiple_testing.csv
For each test it reports whether the bias is predicted detectable (biased function and N >= N*) and whether Holm / BH reject at 0.05.
"""
import csv, glob

rows = []
for f in sorted(glob.glob("results/*/summary.csv")):
    for r in csv.DictReader(open(f)):
        for k in ("p_heavy_test", "p_chi2_B10"):
            v = r.get(k)
            if v in (None, "", "-"):
                continue
            ns = r.get("Nstar") or ""
            # controls are unbiased by construction: their N* refers to the biased counterpart, so nothing is predicted
            pred = (not r["role"].startswith("control")) and ns not in ("", "-", "inf") and float(ns) <= float(r["N"])
            rows.append({"source": r["source"], "file": r["file"], "role": r["role"], "test": k,
                         "N": r["N"], "Nstar": ns, "predicted_detectable": pred, "p": float(v)})
m = len(rows)
order = sorted(range(m), key=lambda i: rows[i]["p"])
stop = False
for rank, i in enumerate(order):                         # Holm step-down
    rej = not stop and rows[i]["p"] <= 0.05 / (m - rank)
    stop = stop or not rej
    rows[i]["holm_reject"] = rej
kmax = max([rank + 1 for rank, i in enumerate(order) if rows[i]["p"] <= 0.05 * (rank + 1) / m] or [0])
for rank, i in enumerate(order):                         # Benjamini-Hochberg
    rows[i]["bh_reject"] = rank < kmax
with open("results/multiple_testing.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows[i] for i in order)
nr = sum(r["holm_reject"] for r in rows); nb = sum(r["bh_reject"] for r in rows)
agree = sum(r["holm_reject"] == r["predicted_detectable"] for r in rows if r["test"] == "p_heavy_test")
nh = sum(r["test"] == "p_heavy_test" for r in rows)
print(f"{m} tests; Holm rejects {nr}, BH rejects {nb}; "
      f"heavy-value test: Holm decision = prediction (N >= N*) in {agree} of {nh}")
for r in (rows[i] for i in order[:max(nr, nb) + 3]):
    print(f"{r['source']:13s} {r['file'][:44]:44s} {r['test']:13s} p={r['p']:<8.3g} N*={r['Nstar']:>9} "
          f"predicted={r['predicted_detectable']!s:5} holm={r['holm_reject']!s:5} bh={r['bh_reject']}")
print("-> results/multiple_testing.csv")
