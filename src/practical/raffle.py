"""E6: a raffle among m participants, winner = rand() % m.
Exact probabilities for Windows rand() (15 bits) and glibc rand() (31 bits), plus a simulation
with the exact Windows model (validated against results/windows-va).
Usage: python src/practical/raffle.py results/<source-id>/practical
"""
import csv, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.practical.msvc_rand import MsvcRand  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
DRAWS = 1_000_000
rows = []
for m in (100, 1000, 20000, 50000):
    for name, w in (("windows-15bit", 15), ("glibc-31bit", 31)):
        W = 2**w
        if m > W:
            continue
        q, r = divmod(W, m)
        p_hi, p_lo = (q + 1) / W, q / W
        never = max(0, m - W) if m > W else 0
        row = {"m": m, "rand": name, "favoured_participants": r,
               "p_favoured": p_hi, "p_other": p_lo if q else 0.0,
               "ratio": (p_hi / p_lo) if q else float("inf"), "fair_p": 1 / m}
        if name.startswith("windows"):
            g = MsvcRand(2026)
            hits = sum(g.rand() % m < r for _ in range(DRAWS))
            row.update({"sim_draws": DRAWS, "sim_share_favoured": hits / DRAWS, "exact_share_favoured": r * p_hi})
        rows.append(row)
    if m > 2**15:  # Windows: participants above 32767 can never win
        rows.append({"m": m, "rand": "windows-15bit", "favoured_participants": 2**15, "p_favoured": 1 / 2**15,
                     "p_other": 0.0, "ratio": float("inf"), "fair_p": 1 / m,
                     "note": f"{m - 2**15} participanti ({(m - 2**15) / m:.0%}) nu pot castiga niciodata"})
fields = ["m", "rand", "favoured_participants", "p_favoured", "p_other", "ratio", "fair_p",
          "sim_draws", "sim_share_favoured", "exact_share_favoured", "note"]
with open(os.path.join(out, "raffle.csv"), "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=fields)
    wr.writeheader()
    wr.writerows(rows)
for r in rows:
    print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
