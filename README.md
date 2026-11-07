# bounded-int-bias

Bias of generating uniform integers in a range {0, …, n−1}: exact theory, statistical tests, and real data from
several languages and environments (C, C++, R, Python, Java, JavaScript, Excel; Linux, macOS, Windows).

Authors: Valentina Astafi, Alexei Leahu — Technical University of Moldova.
Part of the doctoral thesis *Comparative statistical analysis of pseudorandom number generation algorithms used in
various computer applications* (Ch. II, 2.4–2.5); the code will be integrated into StatPRNG.

## In short

With r = 2^w mod n, the methods `floor(n·U)` and `k mod n` give exactly r "heavy" values. The probability gap is
r(n−r)/(n·2^w), and the heavy-value test detects the bias with approximately

N* ≈ (z₁₋α/₂ + z₁₋β)² · 4^w / (r(n−r))

samples. Details and the status of every claim: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

## Results

### R `sample()`, n = 1.5·2^30, 100,000 values (source `linux-cloud`)

| Method | heavy-value test, N = 1,000 | χ² (1,000 classes), N = 100,000 |
|---|---|---|
| `Rounding` (R ≤ 3.5) | p ≈ 10⁻⁵ (detected) | p = 0.93 (not detected) |
| `Rejection` (R ≥ 3.6) | p = 0.11 | p = 0.53 |

### All languages, n = 1.5·2^30, N = 100,000 (`results/linux-cloud/summary.csv`)

| Function | Bits | N* (formula) | p, heavy-value test | Conclusion |
|---|---|---|---|---|
| C `rand() % n` (glibc) | 31 | 63 | ≈ 0 | bias detected |
| R `sample()`, old (`Rounding`) | 32 | 251 | ≈ 0 | bias detected |
| R `sample()`, new (`Rejection`) | — | — | 0.42 | correct |
| Java `nextInt(n)` | — | — | 0.43 | correct |
| Python `randrange`, numpy | — | — | 0.27; 0.13 | correct |
| JS `crypto.randomInt` | — | — | 0.67 | correct |
| Python `int(random()*n)`, Java `(long)(nextDouble()*n)` | 53 | 1.1·10¹⁵ | 0.36; 0.36 | bias exists, practically undetectable |
| JS `Math.floor(Math.random()*n)` | 52 | 2.8·10¹⁴ | 0.92 | bias exists, practically undetectable |

The same conclusions hold on macOS and Windows (`results/mac-va/summary.csv`, `results/windows-va/summary.csv`).

### Reproducibility on three systems, same seed (`results/reproducibility_*.csv`)

| Function | Linux x86-64 (glibc, libstdc++) | macOS arm64 (libc, libc++) | Windows x86-64, Pentium (MinGW: libstdc++) |
|---|---|---|---|
| C++ `uniform_int_distribution` + `mt19937` | reference | **differs from the first value** | identical to Linux |
| C `rand()` | `RAND_MAX` = 2^31−1 | `RAND_MAX` = 2^31−1, different algorithm | **`RAND_MAX` = 32,767** |
| R, Python (random, numpy), Java | reference | identical | identical |

The differences come from the standard library in use, not from the operating system or the processor: Windows with
libstdc++ matches Linux, and R, Python and Java produce the same 100,000 values on x86 and on ARM.

On Windows, `rand() % n` is strongly biased already at n = 20,000 (N* ≈ 91; p ≈ 0), and for n = 1.5·2^30 it only
produces values below 32,768: almost all of the requested range never occurs.

### Practical effect (E6): a raffle among m participants with `rand() % m`

`results/linux-cloud/practical/raffle.csv`; exact model of the Windows `rand()`, validated on all 100,000 values in
`results/windows-va`.

| m | Windows (15 bits) | Linux/macOS (31 bits) |
|---|---|---|
| 1,000 | the first 768 participants have 3.1% higher odds | difference ≈ 0 |
| 20,000 | the first 12,768 participants have **twice** the odds; 64% of participants take 78% of the wins | ratio 1.000009 |
| 50,000 | **17,232 participants (34%) can never win** | ratio 1.000023 |

### Power of the tests (`results/linux-cloud/power/power.csv`)

![Power of the heavy-value test and of chi-square](figures/fig1_power.png)

At N = 4·N* (α = 0.05, 400 replications, mean over 4 values of n):

| Method | heavy-value test | χ² B=10 | χ² B=100 | χ² B=1,000 | χ² B=10,000 |
|---|---|---|---|---|---|
| `mult` (`floor(n·U)`) | 1.00 | ≈ 0.05 | ≈ 0.04 | ≈ 0.05 | ≈ 0.05 |
| `mod` (`k mod n`) | 1.00 | ≈ 0.99 | ≈ 0.65 | ≈ 0.18 | ≈ 0.08 |

For `mult`, equal-class χ² stays at the type I error level whatever the number of classes. For `mod`, the bias is
concentrated at the start of the range and χ² with few classes detects it.

### Where the bias is detectable

![N* as a function of n for different word sizes](figures/fig2_nstar_map.png)

### Standard battery (E7): TestU01 SmallCrush, n = 1.5·2^30, MT19937 seed 2026 (`results/mac-va/testu01`)

| Generator | u = y / n (direct) | u = (y + V) / n (dithered) |
|---|---|---|
| raw MT19937 (control) | 0 of 15 failed | — |
| `rejection` (correct) | **8 failed** (artefact) | 0 failed |
| `mult` (`floor(n·U)`) | 8 failed | 9 failed |
| `mod` (`k mod n`) | 12 failed | 7 failed |
| `mult`, 53-bit source (Python `random()`) | — | 0 failed |
| `mod`, 53-bit source | — | 0 failed |

Feeding y / n directly makes even the correct conversion fail: y / n has only ~30.6 bits and TestU01 reads 32, so
the bit-level tests see the lattice, not the bias. With dithering (V uniform from the next output) the correct
conversion passes and both biased conversions fail. `mod` fails tests on the coarse distribution (MaxOft,
RandomWalk1); `mult` fails only tests that read low-order bits (Gap, SimpPoker, CouponCollector, HammingIndep,
WeightDistrib), because its heavy values repeat with period 3 (y = ⌊3k/8⌋) and equal-width classes average them out.
With a 53-bit source both conversions pass, as predicted by N* ≈ 1.1·10¹⁵.

### Still to run

- E5: Excel (`RANDBETWEEN`, `INT(RAND()*n)`, resolution of `RAND()`) on Windows and macOS.
- E7: Crush (overnight).

## Layout

```
src/theory/bias.py          exact formulas (heavy values, gap, N*)
src/simulation/power.py     power of the tests by simulation
src/analyze_sample.py       analysis of a file of values from ANY source
src/languages/<language>/   generators: C, C++, R, Python, Java, JavaScript, Excel (protocol)
src/practical/              E6: raffle with rand() % m; exact model of the Windows rand()
src/testu01/                E7: TestU01 harness
scripts/                    run_local.sh / .bat, analyze_all.py, compare_sources.py, record_env.py, make_figures.py
results/<source-id>/        data and results, one folder per source (see results/README.md)
figures/                    article figures (PDF + PNG)
tests/                      exhaustive checks of the theory
docs/                       methodology, literature, bibliography
```

## How to reproduce

```bash
pip install -r requirements.txt
python -m pytest -q tests                          # theory, exhaustive for w = 6, 8, 10
sh scripts/run_local.sh <source-id>                # macOS / Linux: all languages found on the machine
scripts\run_local.bat <source-id>                  # Windows
python scripts/analyze_all.py <source-id>          # -> results/<source-id>/summary.csv
python scripts/compare_sources.py <a> <b>          # same-seed reproducibility
python src/simulation/power.py --out results/<source-id>/power --bins 10 100 1000 10000
python src/practical/raffle.py results/<source-id>/practical
python scripts/make_figures.py                     # -> figures/
```

Excel: `src/languages/excel/PROTOCOL.md`. Rules for results: `results/README.md`.

## License

Code: MIT. Data and documentation: CC BY 4.0.
