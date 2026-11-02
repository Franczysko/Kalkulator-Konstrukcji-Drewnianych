# Zasady implementacji obliczeń

Planowany zakres odniesień: PN-EN 1990, PN-EN 1991-1-1, PN-EN 1991-1-3,
PN-EN 1991-1-4, PN-EN 1995-1-1, PN-EN 338 i PN-EN 14250.
Lista nie potwierdza aktualności konkretnych wydań. Przed implementacją ustal
obowiązujące wydanie, zmiany, poprawki oraz właściwe polskie załączniki krajowe
na podstawie autorytatywnych źródeł. Repozytorium nie zawiera treści norm.

Każdy moduł musi dokumentować zakres stosowania, jednostki wejściowe/wyjściowe,
założenia, źródło każdego współczynnika (wydanie, punkt, załącznik), algorytm
oraz ograniczenia. Nie stosuj domyślnych, niepotwierdzonych wartości normowych.
Testy muszą obejmować przypadki graniczne, odrzucanie nieprawidłowych danych
oraz niezależne przykłady referencyjne z uzasadnionymi tolerancjami.
Wynik powinien zawierać wersję metody i danych, dane wejściowe, pośrednie kroki
oraz źródła, tak aby umożliwić niezależne odtworzenie.

Logika domenowa nie importuje React ani kodu interfejsu. Katalogi materials,
loads, combinations, resistance i connections są miejscami na przyszłe moduły.
Na obecnym etapie nie zaimplementowano żadnych obliczeń konstrukcyjnych.
