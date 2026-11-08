"""Figures for the article (PDF for LaTeX + PNG for preview) -> figures/
Usage: python scripts/make_figures.py
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.theory.bias import n_star  # noqa: E402

os.makedirs("figures", exist_ok=True)
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3de"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]   # validated categorical order
MK = ["o", "s", "^", "D", "v"]                                 # secondary encoding (CVD / print)
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "lines.linewidth": 1.6, "savefig.bbox": "tight",
                     "pdf.fonttype": 42, "ps.fonttype": 42})


def save(fig, name):
    fig.savefig(f"figures/{name}.pdf")
    fig.savefig(f"figures/{name}.png", dpi=200)
    plt.close(fig)


# ---- Figure 1: power vs N/N* (mean over n, band = min..max) ----------------------------------
rows = list(csv.DictReader(open("results/linux-cloud/power/power.csv")))
series = [("power_heavy_test", "heavy-value test"), ("power_chi2_B10", "χ², 10 classes"),
          ("power_chi2_B100", "χ², 100 classes"), ("power_chi2_B1000", "χ², 1 000 classes"),
          ("power_chi2_B10000", "χ², 10 000 classes")]
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
for ax, method, title in zip(axes, ("mult", "mod"), ("multiply: ⌊n·k/2ʷ⌋", "modulo: k mod n")):
    sub = [r for r in rows if r["method"] == method]
    fs = sorted({float(r["N_over_Nstar"]) for r in sub})
    for i, (col, lab) in enumerate(series):
        vals = np.array([[float(r[col]) for r in sub if float(r["N_over_Nstar"]) == f] for f in fs])
        ax.fill_between(fs, vals.min(1), vals.max(1), color=C[i], alpha=0.15, linewidth=0)
        ax.plot(fs, vals.mean(1), color=C[i], marker=MK[i], markersize=4, label=lab)
    ax.axhline(0.8, color=MUTED, linestyle="--", linewidth=0.8)
    ax.axhline(0.05, color=MUTED, linestyle=":", linewidth=0.8)
    ax.axvline(1.0, color=GRID, linewidth=0.8, zorder=0)
    ax.set_xscale("log", base=2)
    ax.set_xticks(fs, [f"{f:g}" for f in fs])
    ax.set_xlabel("sample size N / N*")
    ax.set_title(title, fontsize=9, color=INK)
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
axes[0].set_ylabel("power (α = 0.05)")
axes[1].text(fs[-1], 0.81, "0.80", color=MUTED, fontsize=7, ha="right", va="bottom")
axes[1].text(fs[-1], 0.06, "α", color=MUTED, fontsize=7, ha="right", va="bottom")
axes[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
save(fig, "fig1_power")

# ---- Figure 2: N* as a function of n for w = 15, 31, 32, 53 -----------------------------------
fig, ax = plt.subplots(figsize=(7.0, 3.0))
for i, (w, lab) in enumerate([(15, "w = 15 (Windows rand())"), (31, "w = 31 (glibc / macOS rand())"),
                              (32, "w = 32 (MT19937, R ≤ 3.5)"), (53, "w = 53 (double: random(), nextDouble())")]):
    hi = min(2**w - 1, 2**40)
    ns = np.unique(np.logspace(1, np.log10(hi), 1500).astype(np.int64))
    ys = np.array([n_star(int(n), w) for n in ns])
    ok = np.isfinite(ys)
    ax.plot(ns[ok], ys[ok], color=C[i], linewidth=0.8, label=lab)
for N, txt in ((1e6, "10⁶ draws"), (1e9, "10⁹ draws")):
    ax.axhline(N, color=MUTED, linestyle="--", linewidth=0.7)
    ax.text(4e10, N * 2.0, txt, color=MUTED, fontsize=7, ha="center")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_ylim(10, 1e33)
ax.set_xlabel("interval size n")
ax.set_ylabel("N* (samples to detect bias, power 0.8)")
ax.grid(color=GRID, linewidth=0.5)
ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
save(fig, "fig2_nstar_map")
print("figures/fig1_power.{pdf,png}, figures/fig2_nstar_map.{pdf,png}")
