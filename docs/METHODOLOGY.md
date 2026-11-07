# Methodology

Project: bias of generating uniform integers in a range {0, …, n−1}.
Authors: V. Astafi, A. Leahu (Technical University of Moldova). Version: v2, 8 November 2026.

## 1. Research question

In which languages and computing environments does the bias of converting a random number to a range persist, how
large is it, and from what sample size does it become statistically detectable?

## 2. Model

The source produces random words k, uniform on [0, 2^w) (w = number of bits). They are mapped to y ∈ {0, …, n−1}:

| Code | Method | Where it occurs |
|---|---|---|
| `mult` | y = ⌊n·k / 2^w⌋ | `floor(U*n)`, R ≤ 3.5 `sample()`, Excel `INT(RAND()*n)` |
| `mod` | y = k mod n | C `rand() % n` |
| correct | rejection, Lemire | R ≥ 3.6, libstdc++, Python `randrange`, Java `nextInt(n)` |

Let q = ⌊2^w / n⌋ and r = 2^w mod n. Under `mult` and `mod`, exactly **r values** receive q+1 preimages (we call them
"heavy") and the other n−r values receive q. If r = 0, there is no bias.

## 3. Theoretical results

1. **Proportion of heavy values.** Under exact uniformity p₀ = r/n; under the biased method p₁ = r(q+1)/2^w.
2. **Gap** (the same for `mult` and `mod`):

   p₁ − p₀ = r(n − r) / (n · 2^w).

3. **Detectability threshold** of the heavy-value test, at level α and power 1−β:

   N* ≈ (z₁₋α/₂ + z₁₋β)² · 4^w / ( r(n − r) ).

**Status.** (1) and (2) are verified exhaustively for w ∈ {6, 8, 10} and all n (`tests/test_bias.py`).
(3) is a normal approximation, checked numerically by simulation (`results/linux-cloud/power/`); a rigorous proof
with error terms is still to be written. A targeted search found no prior publication of (3) (see
`LITERATURE.md`); the sample-size reasoning itself is standard, so the contribution is the pooled heavy-value test
together with the exact gap (2). The search is to be repeated in Scopus and MathSciNet before submission.

## 4. Statistical tests

- **Heavy-value test.** Count how many samples fall on heavy values; binomial test against p₀.
  Each value is classified exactly, in integer arithmetic (`src/theory/bias.py`).
- **χ² with B equal classes** (comparison), B ∈ {10, 100, 1,000, 10,000}, with exact class probabilities.
- Level α = 0.05; power estimated from 400 replications per combination.

Result (E2, `results/linux-cloud/power/`): for `mult`, equal-class χ² has power ≈ α (0.03–0.07) for
B ∈ {10, 100, 1,000, 10,000}, even at 4·N*, because the heavy values are spread evenly and cancel out within
classes. For `mod`, the heavy values are concentrated at the start of the range and χ² with few classes detects
them (B = 10: power ≈ 0.99 at 4·N*); power falls as B grows (B = 10,000: ≈ 0.08).

## 5. Experimental design

| Step | What | Where | Status |
|---|---|---|---|
| E1 | Validation of the theory (exhaustive, small w) | `tests/` | done |
| E2 | Power of the tests vs. N/N* for several n | `src/simulation/power.py` | done |
| E3 | Real data from languages (C, C++, R old/new, Python, Java, JS) | `src/languages/*` | done on Linux, macOS, Windows |
| E4 | Reproducibility: same seed on different implementations | `scripts/compare_sources.py` | done on three systems |
| E5 | Excel as a black box: `RANDBETWEEN`, `INT(RAND()*n)`, resolution of `RAND()` | `src/languages/excel` | to run (Windows, macOS) |
| E6 | Practical effect: a raffle with `rand() % m` (Windows vs. Linux/macOS) | `src/practical/raffle.py` | done |
| E7 | Does TestU01 (SmallCrush, Crush) detect the bias after conversion: raw MT19937, rejection, `mult`, `mod`, n = 1.5·2^30 | `src/testu01/`, `scripts/run_testu01.sh` | to run (macOS) |

Values of n: common sizes (6, 10, 52, 100, 1,000) and high-bias sizes (large r(n−r), near 2^w / 1.5).

## 6. Protocol for different sources

Each run is made on a **source** identified by a `source-id` (e.g. `linux-cloud`, `mac-va`, `windows-va`,
`excel-win-va`, `excel-mac-va`). For each source:

1. `sh scripts/run_local.sh <source-id>` (or `scripts\run_local.bat` on Windows) runs every installed language and
   writes `results/<source-id>/environment.json` (system, versions, CPU, date).
2. Raw data go to `results/<source-id>/<experiment>/`, compressed to `.gz` when large; file names contain the
   method, n, N and the seed.
3. The same analysis is applied to every source: `python scripts/analyze_all.py <source-id>`.
4. Results are never edited by hand. A faulty run is redone, not corrected.

## 7. Reproducibility

- Default seed 2026; all seeds appear in file names or in `params.json`.
- Versions are recorded automatically (step 1 above).
- Python environment: `requirements.txt`.
