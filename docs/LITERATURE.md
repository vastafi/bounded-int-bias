# Literature

Checked against the original sources on 7–8 November 2026. Full BibTeX: `references.bib`.

| Work | What it establishes | What this project adds |
|---|---|---|
| Knuth 1997, TAOCP vol. 2 | Quantisation theorem for ⌊mX⌋ | — (starting point) |
| Ottoboni & Stark 2018, arXiv:1809.06520 (preprint) | Worst case: ratio ≈ 1 + m·2^(−w+1); the bias in R ≤ 3.5 | Exact bias for every n; detectability threshold |
| R Core 2019, R 3.6.0 NEWS | `sample.kind` changed to `Rejection` | Empirical check, old vs. new |
| Lemire 2019, ACM TOMACS 29(1), doi:10.1145/3230636 | Fast unbiased method | Control: real implementations are correct |
| Quaglia 2019, ACM TOMACS 29(1), doi:10.1145/3239569 | Replication report for Lemire 2019 | Model for reproducibility |
| Brackett-Rozinsky & Lemire 2025, SPE 55(1), doi:10.1002/spe.3369 | Lemire's method adopted in libstdc++, MSVC, Linux, Go, Swift, Julia, C#, Zig | Hand-written idioms are not covered |
| O'Neill 2018, pcg-random.org (blog) | Comparison of methods, including bias | Formal statistics and power |
| Hořeňovský 2020, WG21 P2059R0 | `uniform_int_distribution` differs between implementations | Measured on three systems |
| McCullough 2008, CSDA 52(10), doi:10.1016/j.csda.2008.03.006 | The Excel generator is not Wichmann–Hill | `RANDBETWEEN`, Windows vs. macOS |
| McCullough & Heiser 2008, CSDA 52(10) | Statistical errors in Excel 2007 | — |
| L'Ecuyer & Simard 2007, ACM TOMS 33, doi:10.1145/1268776.1268777 | TestU01 | Does TestU01 detect conversion bias? |
| Matsumoto & Nishimura 1998, ACM TOMACS 8 | Mersenne Twister | — (the base generator) |
| Goualard 2022, ACM TOMACS 32(3), doi:10.1145/3503512 | Floating-point numbers in an interval | Possible extension |

## Novelty check of N* (8 November 2026)

Targeted web search (three extended queries). The closest sources:

| Source | What it has | Difference from this project |
|---|---|---|
| Cook 2018, blog | Sample size to tell **two** values apart: ≈ 8(p₁+p₂)/(p₁−p₂)²; for n = 52 it gives ≈ 6·10¹⁸ | We pool all r heavy values; the required sample size falls about 7-fold at n = 52 and about 7·10⁸-fold at n = 1.6·10⁹ |
| Banić & Elezović, arXiv:2606.01465 | Uniformity test for structured alternatives (period 2), motivated by quantisation | Different structure; covers neither modulo/multiply nor the required sample size |

Conclusion: no prior publication of N* was found. The sample-size reasoning (two proportions) is standard, so the
contribution should be presented as **the test that pools the heavy values + the exact gap r(n−r)/(n·2^w)**, not as a
new sample-size formula in itself. A web search does not prove novelty; it is to be repeated in Scopus and
MathSciNet before submission.

## To do

- Database search (Scopus, MathSciNet) for N* and for pooled tests of quantisation bias.
- High-power tests of discrete uniformity against structured alternatives.
