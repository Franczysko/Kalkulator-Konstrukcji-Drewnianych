# Praca nad skoroszytem

Formuły dostarczonego XLSX muszą działać bez Pythona i bez zewnętrznych plików.
Generator jest w src/generate.py, niezależna implementacja kontrolna w src/frame.py.
Nie dodawaj domyślnych współczynników normowych bez źródła, wydania, punktu i NA.
Nie zmieniaj statusu na SPEŁNIA, gdy istotne sprawdzenie pozostaje niewykonane.
Po zmianach obliczeń lub generatora uruchom `python excel/tests/run.py` z katalogu
repozytorium (wymaga LibreOffice Calc i zależności excel/requirements.txt).
Sprawdź PDF kart DANE i RAPORT oraz brak błędów Excela, nie tylko składnię formuł.
Testy muszą sprawdzać niezależne wzorce, znaki, równowagę i reakcję na zmianę danych.
Nie publikuj załączonych norm ani arkusza wzorcowego. Źródła identyfikuj metadanymi
i sumami SHA-256. Utrzymuj uczciwy rejestr funkcji niezweryfikowanych.
