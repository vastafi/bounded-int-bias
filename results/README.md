# Rezultate

Câte un dosar pe **sursă** (`source-id`), toate cu aceeași structură:

```
results/<source-id>/
├── environment.json        sistem, versiuni, data (scripts/record_env.py; la Excel, completat de mână)
├── cpp-uniform/            E4: std::uniform_int_distribution, același seed
│   ├── cpp_uniform_n1000_N20_seed2026.txt
│   ├── library.txt         libstdc++ / libc++ / MSVC
│   └── compiler.txt
├── c-randmod/              E3: rand() % n
│   ├── c_randmod_n20000_N100000_seed2026.txt
│   ├── c_randmod_n1610612736_N100000_seed2026.txt
│   └── rand_max.txt
├── python-sample/          E3: randrange, int(random()*n), numpy (dacă e instalat Python)
├── r-sample/               E3: R sample(), metodele Rounding și Rejection (dacă e instalat R)
├── java-sample/            E3: nextInt(n), (long)(nextDouble()*n) (dacă e instalat Java)
├── js-sample/              E3: Math.floor(Math.random()*n), crypto.randomInt (dacă e instalat Node.js)
├── summary.csv             analiza tuturor fișierelor: python scripts/analyze_all.py <source-id>
├── power/                  E2: simularea puterii (doar linux-cloud)
├── testu01/                E7: SmallCrush/Crush pe generatorul brut și pe trei conversii (sh scripts/run_testu01.sh)
└── excel-sample/           E5: doar la sursele excel-*
```

| source-id | Cine rulează | Cum |
|---|---|---|
| `linux-cloud` | Claude | `sh scripts/run_local.sh linux-cloud` + simulare |
| `mac-va` | V. Astafi | `sh scripts/run_local.sh mac-va` |
| `windows-va` | V. Astafi | `scripts\run_local.bat windows-va` |
| `excel-win-va`, `excel-mac-va` | V. Astafi | `src/languages/excel/PROTOCOL.md` |

Comparația a două surse cu același seed: `python scripts/compare_sources.py <a> <b>` →
`results/reproducibility_<a>_vs_<b>.csv`.

Dacă pe o sursă nu există Python, scriptul scrie `environment.txt` în loc de `environment.json`; Claude îl
convertește la import, ca toate sursele să aibă același format.

Reguli: numele fișierelor conțin metoda, n, N și seed-ul; rezultatele nu se editează de mână; o rulare greșită
se reface integral și se înlocuiește printr-un commit separat, cu explicația în mesajul de commit.
