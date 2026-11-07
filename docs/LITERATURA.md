# Literatura (etapa G1)

Verificată la sursă pe 7 noiembrie 2026. BibTeX complet: `references.bib`.

| Lucrare | Ce stabilește | Ce adaugă proiectul |
|---|---|---|
| Knuth 1997, TAOCP vol. 2 | Teorema de cuantizare pentru ⌊mX⌋ | — (punct de plecare) |
| Ottoboni & Stark 2018, arXiv:1809.06520 (preprint) | Cazul cel mai rău: raport ≈ 1 + m·2^(−w+1); biasul din R ≤ 3.5 | Bias exact pentru orice n; prag de detectabilitate |
| R Core 2019, NEWS R 3.6.0 | Schimbarea `sample.kind` în `Rejection` | Verificare empirică veche vs. nouă |
| Lemire 2019, ACM TOMACS 29(1), doi:10.1145/3230636 | Metodă rapidă și nedeplasată | Control: implementările reale sunt corecte |
| Quaglia 2019, ACM TOMACS 29(1), doi:10.1145/3239569 | Raport de reproducere pentru Lemire 2019 | Model de reproductibilitate |
| Brackett-Rozinsky & Lemire 2025, SPE 55(1), doi:10.1002/spe.3369 | Metoda Lemire adoptată în libstdc++, MSVC, Linux, Go, Swift, Julia, C#, Zig | Formulele scrise de mână nu sunt acoperite |
| O'Neill 2018, pcg-random.org (blog) | Comparație de metode, inclusiv bias | Statistică formală și putere |
| Hořeňovský 2020, WG21 P2059R0 | `uniform_int_distribution` diferă între implementări | Măsurarea divergenței |
| McCullough 2008, CSDA 52(10), doi:10.1016/j.csda.2008.03.006 | Generatorul din Excel nu e Wichmann–Hill | `RANDBETWEEN`, Windows vs. Mac |
| McCullough & Heiser 2008, CSDA 52(10) | Erori statistice în Excel 2007 | — |
| L'Ecuyer & Simard 2007, ACM TOMS 33, doi:10.1145/1268776.1268777 | TestU01 | Detectează TestU01 biasul de conversie? |
| Matsumoto & Nishimura 1998, ACM TOMACS 8 | Mersenne Twister | — (generatorul de bază) |
| Goualard 2022, ACM TOMACS 32(3), doi:10.1145/3503512 | Numere reale într-un interval | Extindere posibilă |

## De făcut

- Căutare țintită: formula N* (secțiunea 3 din METODOLOGIE) a mai fost publicată?
- Teste de uniformitate discretă cu putere ridicată pentru alternative structurate.
