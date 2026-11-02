# Rozpoznane źródła i przyjęta podstawa historyczna

Stan analizy: 2 listopada 2026 r. Nie potwierdzono aktualnego katalogu PKN:
żądanie HEAD do https://sklep.pkn.pl/ przez skonfigurowany proxy otrzymało 403.
Nie zastępowano tej kontroli domysłami o aktualności pierwszej lub drugiej generacji.

| Źródło użytkownika | Rozpoznanie | Użycie |
|---|---|---|
| PN-EN 1995-1-1 2010.pdf | 130 stron; skan. Przedmowa krajowa: EN 1995-1-1:2004+AC:2006+A1:2008. Zawiera NA na stronach PDF 2–3 | Ręcznie odczytane współczynniki i częściowe kontrole; bez deklaracji aktualności |
| PN-EN 338 (1999) — Drewno konstrukcyjne klasy.pdf | 8 stron; tablica 1 strona 7 | C18/C24/C30: historyczne fm, ft0, fc0, fv, Emean, E05, Gmean, ρmean |
| EUF424_1.PDF | 42 strony; okładka OCR: PN-EN 1991-1-1:2004 | Tylko identyfikacja; nie implementowano tabel ciężarów |
| Eurokod_1…Obciążenie_śniegiem.pdf | 54 strony; okładka OCR: PN-EN 1991-1-3:2005 | Tylko identyfikacja; wejście S określa projektant |
| Eurokod_1…Oddziaływanie_wiatru.pdf | 152 strony; brak warstwy tekstowej | Bez wyznaczania parametrów normowych; W+/W− podaje projektant |
| Dokumentacje ETA / DoP w RAR | ETA-04/0013, ETA-20/1284, ETA-21/0482 i deklaracje produktów | Nie przyjmowano uniwersalnych nośności płytek ani mocowań |
| Gable panel stud design EC5.xlsx | Flatwise timber, Edgewise timber, Value | Wzorzec wyglądu. Nie traktowano jako źródła polskiego NA |
| PN-EN 1990 / NA | Brak dostarczonego pełnego źródła | γG/γQ/ψ0/ψ2 pozostawione puste |
| PN-EN 14250 | Brak potwierdzonego wydania | Niewdrożona kontrola prefabrykacji i płytek |

Dwie serie sześciu części RAR mają identyczne sumy SHA-256. Archiwum odczytano
jako zestaw woluminów, nie przez arbitralne sklejanie plików. PDF-y wyodrębniono
poza repozytorium. Wymienione źródła identyfikuje manifest `sources.json`.
Pełnych norm, katalogów producentów i wzorcowego skoroszytu nie wysłano na GitHub.

## Odczytane klauzule EC5

- PDF str. 2: NA.1 — śnieg średniotrwały, wiatr krótkotrwały; NA.2 — γM.
- PDF str. 29 (druk str. 23): 2.4.1, wzór (2.14), Xd=kmod Xk/γM.
- PDF str. 30: tab. 2.3, γM drewno lite 1.3.
- PDF str. 33–34: tab. 3.1 i 3.2, kmod i kdef.
- PDF str. 44 (druk str. 38): 6.1.6, km=0.7 dla prostokąta.
- PDF str. 47 (druk str. 41): 6.2.3 i 6.2.4, interakcje (6.17)–(6.20).
- PDF str. 48–49: stateczność 6.3.2/6.3.3 — rozpoznana, **niezaimplementowana**.
- 9.2.4: przepony ścienne — **niezaimplementowane**, bez ekstrapolowania na szczyty.

OCR służył do wyszukiwania klauzul. Kluczowe równania i współczynniki sprawdzono
na obrazach stron; nie kopiowano błędnego znaku pod pierwiastkiem z arkusza
wzorcowego ani jego współczynnika kmod=1.1 dla wiatru.

## Dane potrzebne do wydania projektowego

Potwierdzone aktualne wydania PN-EN, zmiany, poprawki i polskie NA tworzące spójny
zestaw; dane materiałowe właściwego wydania PN-EN 338; dokumentacje konkretnego
poszycia, łączników, kotew i podłoża; uzasadnione stopnie swobody i sztywności
złączy; przykłady referencyjne dla stateczności oraz wybranej metody przepony.
