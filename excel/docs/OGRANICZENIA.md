# Rejestr ograniczeń — wersja 0.2

| Zakres | Stan |
|---|---|
| Aktualność PKN na 2026 r. | Niepotwierdzona; próba https://sklep.pkn.pl/ otrzymała 403 z proxy |
| PN-EN 1990 i polski NA | Brak pełnego źródła; współczynniki puste, generator nieaktywny do uzupełnienia |
| Baza drewna | PN-EN 338:1999; wymaga zastąpienia danymi przyjętego aktualnego zestawu |
| Geometria ściany | Tylko 3 słupki; brak dowolnej liczby słupków, otworów, rygli i zastrzałów |
| Geometria wysuwnicy | Tylko 2 podłużnice × 3 stacje; brak dowolnej topologii |
| Połączenia prętów | Wyłącznie sztywne; brak zwolnień końcowych i sprężyn |
| Podpory | Dwustronne, idealnie sztywne blokady DOF; brak odrywania/kontaktu |
| Rzeczywiste mocowanie | Nie zweryfikowano sztywności ani nośności przyjętych podpór |
| Przepony i poszycie | Brak analizy 9.2.4, OSB nie jest traktowane jako stężenie |
| Rozdział powierzchniowy | Zadany schemat pasm; nie model powłokowy ani zweryfikowany model współpracy płyt |
| Stateczność | Brak wyboczenia, zwichrzenia, imperfekcji, II rzędu i stateczności całego układu |
| Ścinanie / skręcanie | Siły obliczone; nośność i interakcje nieweryfikowane |
| Połączenia, kotwy, płytki | Obliczane działania; brak sprawdzenia nośności produktu i podłoża |
| Wpływ poślizgu złączy | Pominięty; nie wolno utożsamiać ugięcia ramy z rzeczywistym ugięciem prefabrykatu |
| SGN | Kandydaci 6.10; brak pełnej obwiedni wszystkich sytuacji i podzbiorów oddziaływań |
| SGU | Tylko dwa stany dla S prowadzącego i W+ towarzyszącego; brak pełnej obwiedni |
| Limit u | Domyślne 10 mm to przykład wejścia, nie wartość normowa |
| Ugięcia | Norma wektora w 21 punktach/pręt, względem układu globalnego |
| Optymalizacja | Brak automatycznego doboru / sugestii przekrojów |
| Raport | Raport częściowy A4; nie zastępuje podpisanej dokumentacji projektowej |
| Testy normowe | Brak kompletnych niezależnych przykładów dla wszystkich mechanizmów zniszczenia |
| Microsoft Excel 365 | Formuły zgodne ze standardowymi funkcjami; brak rzeczywistego uruchomienia Microsoft Excel w tej sesji |

Wynik globalny pozostaje NIEZWERYFIKOWANE mimo pozytywnej częściowej kontroli
przekroju. Wykryte przekroczenie aktywnego SGN daje NIE SPEŁNIA. Uszkodzone lub
niekompletne wejścia nie są zastępowane normowymi wartościami domyślnymi.
Nie stwierdzono gotowości do samodzielnej, rzeczywistej pracy projektowej.

Do wydania projektowego potrzebne są potwierdzone aktualne źródła norm i NA,
uzasadnione modele połączeń/podpór, dane produktów oraz weryfikacja brakujących
mechanizmów przez uprawnionego projektanta. Nie wymaga to publikowania pełnych
tekstów norm w repozytorium.
