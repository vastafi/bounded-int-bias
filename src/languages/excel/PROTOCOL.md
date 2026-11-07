# Protocol Excel (Windows și Mac)

Excel nu are seed, deci fiecare rulare e o sursă nouă. Înregistrăm versiunea exactă (Fișier → Cont → Despre Excel).

## E5a. `RANDBETWEEN` cu n de bias mare

1. Foaie nouă. În A1: `=RANDBETWEEN(0;1610612735)` (pe setări englezești separatorul e `,`).
2. Copiază A1 în A1:A100000.
3. Copiază coloana și lipește **doar valorile** (Paste Special → Values), ca să nu se recalculeze.
4. Salvează ca text, o valoare pe linie: `excel_randbetween_n1610612736_N100000.txt`.

## E5b. `INT(RAND()*n)`

La fel, cu formula `=INT(RAND()*1610612736)`. Fișier: `excel_intrand_n1610612736_N100000.txt`.

## E5c. Rezoluția lui `RAND()`

1. În A1:A100000: `=RAND()`, apoi lipire ca valori.
2. Formatează coloana cu 17 zecimale și salvează ca text (`excel_rand_N100000.txt`).
   Din valori se estimează câți biți are generatorul (numitorul comun minim).

## Unde pui fișierele (aceeași structură ca la celelalte surse)

```
results/excel-win-va/                 (pe Mac: results/excel-mac-va/)
├── environment.json                  copiat din src/languages/excel/environment_template.json și completat
└── excel-sample/
    ├── excel_randbetween_n1610612736_N100000.txt
    ├── excel_intrand_n1610612736_N100000.txt
    └── excel_rand_N100000.txt
```

Analiza o face Claude cu același script ca pentru restul surselor:
`python src/analyze_sample.py <fișier> --n 1610612736 --method mult --w 32` (w se ajustează după E5c).
