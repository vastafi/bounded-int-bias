# bounded-int-bias

Biasul generării întregilor uniformi într-un interval {0, …, n−1}: teorie, teste statistice și date reale din
mai multe limbaje și medii de calcul (R, C, C++, Python, Java, JavaScript, Excel; Linux, macOS, Windows).

Autori: Valentina Astafi, Alexei Leahu — Universitatea Tehnică a Moldovei.
Parte a tezei de doctorat *Analiza statistică comparativă a algoritmilor de generare a numerelor pseudoaleatoare
folosiți în diverse aplicații pe calculator* (cap. II, 2.4–2.5); codul va fi integrat în StatPRNG.

## Pe scurt

Cu r = 2^w mod n, metodele `floor(n·U)` și `k mod n` dau exact r valori „grele”. Diferența de probabilitate
este r(n−r)/(n·2^w), iar testul pe valori grele detectează biasul cu aproximativ

N* ≈ (z₁₋α/₂ + z₁₋β)² · 4^w / (r(n−r))

eșantioane. Detalii și statutul fiecărei afirmații: [`docs/METODOLOGIE.md`](docs/METODOLOGIE.md).

## Rezultate (sursa `linux-cloud`)

**R `sample()`, n = 1,5·2^30, 100 000 de valori**

| Metoda | test pe valori grele, N = 1 000 | χ² (1 000 clase), N = 100 000 |
|---|---|---|
| `Rounding` (R ≤ 3.5) | p ≈ 10⁻⁵ (detectat) | p = 0,93 (nedetectat) |
| `Rejection` (R ≥ 3.6) | p = 0,11 | p = 0,54 |

**Puterea testelor la N = 4·N\*** (α = 0,05, 400 de repetări; valori medii pe 4 valori ale lui n)

| Metoda | test pe valori grele | χ² B=10 | χ² B=100 | χ² B=1 000 | χ² B=10 000 |
|---|---|---|---|---|---|
| `mult` (`floor(n·U)`) | 1,00 | ≈ 0,05 | ≈ 0,04 | ≈ 0,05 | ≈ 0,05 |
| `mod` (`k mod n`) | 1,00 | ≈ 0,99 | ≈ 0,65 | ≈ 0,18 | ≈ 0,08 |

La `mult`, χ² cu clase egale rămâne la nivelul erorii de tip I indiferent de numărul de clase. La `mod`, biasul
este grupat la începutul intervalului și χ² cu puține clase îl detectează. Date complete:
`results/linux-cloud/power/power.csv`.

## Structura

```
src/theory/bias.py          formulele exacte (valori grele, diferență, N*)
src/simulation/power.py     puterea testelor prin simulare
src/analyze_sample.py       analiza unui fișier de valori din ORICE sursă
src/languages/<limbaj>/     generatoare: R, C, C++, Excel (protocol), ...
scripts/record_env.py       înregistrează sistemul și versiunile unei surse
results/<source-id>/        date și rezultate, câte un dosar pe sursă
tests/                      verificări exhaustive ale teoriei
docs/                       metodologie, literatură, bibliografie
```

## Cum reproduci

```bash
pip install -r requirements.txt
python -m pytest -q tests
python scripts/record_env.py <source-id>
Rscript src/languages/r/sample_r.R 1610612736 100000 2026 results/<source-id>/r-sample
python src/analyze_sample.py results/<source-id>/r-sample/<fișier> --n 1610612736 --method mult
python src/simulation/power.py --out results/<source-id>/power --bins 10 100 1000 10000
```

Pentru C/C++ pe Mac sau Linux: `sh scripts/run_local.sh <source-id>`; pe Windows: `scripts\run_local.bat <source-id>`.
Pentru Excel: `src/languages/excel/PROTOCOL.md`. Regulile pentru rezultate: `results/README.md`.

## Licență

Cod: MIT. Date și documentație: CC BY 4.0.
