# Rezultate

Câte un dosar pe **sursă** (`source-id`): `linux-cloud`, `mac-va`, `windows-va`, `excel-win-va`, `excel-mac-va`.

Fiecare dosar conține:
- `environment.json` — sistem, versiuni, data (generat cu `scripts/record_env.py`; pentru Excel, completat de mână);
- câte un subdosar pe experiment (`r-sample/`, `power/`, `cpp-uniform/`, ...), cu datele brute (`.txt.gz`) și
  rezultatele analizei (`.json`, `.csv`).

Reguli: numele fișierelor conțin metoda, n, N și seed-ul; rezultatele nu se editează de mână; o rulare greșită
se reface integral și se înlocuiește printr-un commit separat, cu explicația în mesajul de commit.
