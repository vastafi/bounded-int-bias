# Excel protocol (Windows and macOS)

Excel has no seed, so every run is a new source. Record the exact version (File → Account → About Excel).

## E5a. `RANDBETWEEN` with a high-bias n

1. New sheet. In A1: `=RANDBETWEEN(0;1610612735)` (with English regional settings the separator is `,`).
2. Copy A1 to A1:A100000.
3. Copy the column and paste **values only** (Paste Special → Values), so that it does not recalculate.
4. Save as text, one value per line: `excel_randbetween_n1610612736_N100000.txt`.

## E5b. `INT(RAND()*n)`

Same procedure with the formula `=INT(RAND()*1610612736)`. File: `excel_intrand_n1610612736_N100000.txt`.

## E5c. Resolution of `RAND()`

1. In A1:A100000: `=RAND()`, then paste as values.
2. Format the column with 17 decimals and save as text (`excel_rand_N100000.txt`).
   The number of bits of the generator is estimated from the values (smallest common denominator).

## Where the files go (same layout as the other sources)

```
results/excel-win-va/                 (on macOS: results/excel-mac-va/)
├── environment.json                  copied from src/languages/excel/environment_template.json and filled in
└── excel-sample/
    ├── excel_randbetween_n1610612736_N100000.txt
    ├── excel_intrand_n1610612736_N100000.txt
    └── excel_rand_N100000.txt
```

Analysis, with the same script as for every other source:
`python scripts/analyze_all.py excel-win-va` (w is adjusted after E5c).
