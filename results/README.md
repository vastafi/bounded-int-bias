# Results

One folder per **source** (`source-id`), all with the same layout:

```
results/<source-id>/
├── environment.json        system, versions, CPU, date (scripts/record_env.py; filled in by hand for Excel)
├── cpp-uniform/            E4: std::uniform_int_distribution, same seed
│   ├── cpp_uniform_n1000_N20_seed2026.txt
│   ├── library.txt         libstdc++ / libc++ / MSVC
│   └── compiler.txt
├── c-randmod/              E3: rand() % n
│   ├── c_randmod_n20000_N100000_seed2026.txt.gz
│   ├── c_randmod_n1610612736_N100000_seed2026.txt.gz
│   └── rand_max.txt
├── python-sample/          E3: randrange, int(random()*n), numpy (if Python is installed)
├── r-sample/               E3: R sample(), Rounding and Rejection methods (if R is installed)
├── java-sample/            E3: nextInt(n), (long)(nextDouble()*n) (if Java is installed)
├── js-sample/              E3: Math.floor(Math.random()*n), crypto.randomInt (if Node.js is installed)
├── summary.csv             analysis of every file: python3 scripts/analyze_all.py <source-id>
├── power/                  E2: power simulation (linux-cloud only)
├── practical/              E6: raffle with rand() % m (linux-cloud only)
├── testu01/                E7: SmallCrush/Crush on the raw generator and three conversions (sh scripts/run_testu01.sh)
└── excel-sample/           E5: excel-* sources only
```

| source-id | Run by | How |
|---|---|---|
| `linux-cloud` | automated (cloud Linux) | `sh scripts/run_local.sh linux-cloud` + simulations |
| `mac-va` | V. Astafi | `sh scripts/run_local.sh mac-va` |
| `windows-va` | V. Astafi | `scripts\run_local.bat windows-va` |
| `excel-win-va`, `excel-mac-va` | V. Astafi | `src/languages/excel/PROTOCOL.md` |

Comparing two sources that used the same seed: `python3 scripts/compare_sources.py <a> <b>` →
`results/reproducibility_<a>_vs_<b>.csv`.

If a source has no Python, the script writes `environment.txt` instead of `environment.json`; convert it to JSON
before committing, so that every source has the same format.

Rules: file names contain the method, n, N and the seed; results are never edited by hand; a faulty run is redone in
full and replaced in a separate commit, with the reason in the commit message.
