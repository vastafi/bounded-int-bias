# Metodologie

Proiect: biasul generării întregilor uniformi într-un interval {0, …, n−1}.
Autori: V. Astafi, A. Leahu (UTM). Versiune: v1, 7 noiembrie 2026.

## 1. Întrebarea de cercetare

În ce limbaje și medii de calcul persistă biasul la conversia unui număr aleator într-un interval, cât de mare este
și de la ce volum de eșantion devine detectabil statistic?

## 2. Modelul

Sursa produce cuvinte aleatoare k uniforme pe [0, 2^w) (w = numărul de biți). Le transformăm în y ∈ {0, …, n−1}:

| Cod | Metodă | Unde apare |
|---|---|---|
| `mult` | y = ⌊n·k / 2^w⌋ | `floor(U*n)`, R ≤ 3.5 `sample()`, Excel `INT(RAND()*n)` |
| `mod` | y = k mod n | C `rand() % n` |
| corect | respingere, Lemire | R ≥ 3.6, libstdc++, Python `randrange`, Java `nextInt(n)` |

Fie q = ⌊2^w / n⌋ și r = 2^w mod n. La `mult` și `mod`, exact **r valori** primesc q+1 preimagini (le numim
„grele”), iar celelalte n−r primesc q. Dacă r = 0, nu există bias.

## 3. Rezultatele teoretice

1. **Proporția valorilor grele.** Sub uniformitate perfectă p₀ = r/n; sub metoda deplasată p₁ = r(q+1)/2^w.
2. **Diferența** (aceeași pentru `mult` și `mod`):

   p₁ − p₀ = r(n − r) / (n · 2^w).

3. **Pragul de detectabilitate** al testului pe valori grele, la nivel α și putere 1−β:

   N* ≈ (z₁₋α/₂ + z₁₋β)² · 4^w / ( r(n − r) ).

**Statut:** (1) și (2) sunt verificate exhaustiv pentru w ∈ {6, 8, 10} și toate n (`tests/test_bias.py`).
(3) este o aproximare normală, verificată numeric prin simulare (`results/linux-cloud/power/`);
demonstrația riguroasă, cu termenii de eroare, rămâne de scris. Noutatea formulei (3) **nu este încă verificată**
în literatură.

## 4. Testele statistice

- **Testul pe valori grele (adaptat).** Numărăm câte eșantioane cad pe valori grele; test binomial față de p₀.
  Clasificarea unei valori se face exact, în aritmetică întreagă (`src/theory/bias.py`).
- **χ² cu B clase egale** (comparație), B ∈ {10, 100, 1 000, 10 000}, cu probabilitățile exacte ale claselor.
- Nivel α = 0,05; putere estimată din 400 de repetări pe combinație.

Rezultat (E2, `results/linux-cloud/power/`): pentru `mult`, χ² cu clase egale are putere ≈ α (0,03–0,07) pentru
B ∈ {10, 100, 1 000, 10 000}, chiar la 4·N*, pentru că valorile grele sunt împrăștiate uniform și se compensează în
clase. Pentru `mod`, valorile grele sunt grupate la început, iar χ² cu puține clase le detectează (B = 10: putere
≈ 0,99 la 4·N*); puterea scade când B crește (B = 10 000: ≈ 0,08).

## 5. Designul experimentului

| Pas | Ce | Unde |
|---|---|---|
| E1 | Validarea teoriei (exhaustiv, w mic) | `tests/` |
| E2 | Puterea testelor vs. N/N* pentru mai multe n | `src/simulation/power.py` |
| E3 | Date reale din limbaje (R vechi/nou, C, C++, Python, Java, JS) | `src/languages/*` |
| E4 | Reproductibilitatea: același seed pe implementări C++ diferite | `src/languages/cpp` (Linux libstdc++, Mac libc++) |
| E5 | Excel ca „cutie neagră”: `RANDBETWEEN`, `INT(RAND()*n)`, rezoluția lui `RAND()` | `src/languages/excel` (Windows, Mac) |
| E6 | Efect practic: tragere la sorți cu `rand() % m` (Windows vs. Linux/Mac) | `src/practical/raffle.py` |
| E7 | Dacă TestU01 (SmallCrush, Crush) prinde biasul după conversie: MT19937 brut, respingere, `mult`, `mod`, n = 1,5·2^30 | `src/testu01/`, `scripts/run_testu01.sh` (rulat pe Mac) |

Valori n: uzuale (6, 10, 52, 100, 1 000) și cu bias mare (r(n−r) mare, aproape de 2^w / 1,5).

## 6. Protocolul pentru surse diferite

Fiecare rulare se face pe o **sursă** identificată printr-un `source-id` (de ex. `linux-cloud`, `mac-va`,
`windows-va`, `excel-win-va`, `excel-mac-va`). Pentru fiecare sursă:

1. `python scripts/record_env.py <source-id> --note "..."` scrie `results/<source-id>/environment.json`
   (sistem, versiuni, data).
2. Datele brute merg în `results/<source-id>/<experiment>/`, comprimate `.gz` dacă sunt mari; numele fișierului
   conține metoda, n, N și seed-ul.
3. Analiza se face cu același script pentru toate sursele:
   `python src/analyze_sample.py <fișier> --n <n> --method mult|mod --json <rezultat>.json`.
4. Rezultatele nu se editează de mână. O rulare greșită se reface, nu se corectează.

## 7. Reproductibilitate

- Seed implicit 2026; toate seed-urile apar în numele fișierelor sau în `params.json`.
- Versiunile se înregistrează automat (pasul 1 de mai sus).
- Mediul Python: `requirements.txt`.
