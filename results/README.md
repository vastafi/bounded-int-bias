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
├── r-sample/               E3: R sample(), metodele Rounding și Rejection (unde există R)
├── power/                  E2: simularea puterii (doar linux-cloud)
└── excel-sample/           E5: doar la sursele excel-*
```

| source-id | Cine rulează | Cum |
|---|---|---|
| `linux-cloud` | Claude | `sh scripts/run_local.sh linux-cloud` + R + simulare |
| `mac-va` | V. Astafi | `sh scripts/run_local.sh mac-va` |
| `windows-va` | V. Astafi | `scripts\run_local.bat windows-va` |
| `excel-win-va`, `excel-mac-va` | V. Astafi | `src/languages/excel/PROTOCOL.md` |

Dacă pe o sursă nu există Python, scriptul scrie `environment.txt` în loc de `environment.json`; Claude îl
convertește la import, ca toate sursele să aibă același format.

Reguli: numele fișierelor conțin metoda, n, N și seed-ul; rezultatele nu se editează de mână; o rulare greșită
se reface integral și se înlocuiește printr-un commit separat, cu explicația în mesajul de commit.
