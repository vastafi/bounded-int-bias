# Excel protocol (Windows and macOS)

Excel has no seed, so every run is a new source. Record the exact version (File → Account → About Excel).

## Quick way (recommended): the ready-made workbook

1. Open `src/languages/excel/E5_template.xlsx` in Excel. Columns A, B, C hold 100,000 rows of
   `RANDBETWEEN(0,1610612735)`, `INT(RAND()*1610612736)` and `RAND()` (17 decimals).
2. File → Save As → **CSV (Comma delimited) (*.csv)**, name `E5.csv`. The CSV keeps the computed values.
3. Convert it into the three sample files below:
   `python3 scripts/import_excel_csv.py path/to/E5.csv excel-win-va` (on macOS: `excel-mac-va`).
4. Fill in `environment.json` (see below) and run the analysis.
5. Resolution of `RAND()`: also save the workbook itself (File → Save, `.xlsx`). Excel stores the exact doubles, and
   `python3 scripts/excel_rand_bits.py path/to/E5_template.xlsx <source-id>` writes `excel_rand_exact_N100000.txt`
   and `rand_bits.txt` (how many fixed-point bits the values use, against the 53-bit uniform expectation).
   Do not test the bits inside Excel with "=": Excel compares with about 15 significant digits, which makes
   values look coarser than they are. The CSV keeps only about 10 significant digits on macOS.

The manual steps E5a–E5c below give the same files.

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
