# Wyniki rzeczywistych testów — 2026-11-02

Silnik arkusza: LibreOffice Calc 25.2.3.2. Generator: Python 3.12, XlsxWriter 3.2.9;
odczyt OpenPyXL 3.1.5; niezależny solver NumPy 2.3.5. Nie uruchamiano Microsoft Excel 365.

## Wzorce analityczne

L=3000 mm, b=45 mm, h=145 mm, E=11000 N/mm², G=690 N/mm².
W próbie skręcania zadano J=10⁶ mm⁴. To testy mechaniki, nie przykłady normowego
projektu. Oczekiwane ugięcia wynikają z osobnych wzorów analitycznych.

| Test | Oczekiwane | Uzyskane | Maks. różnica |
|---|---|---|---|
| cantilever tip force deflection | -71.5672862952 | -71.5672862952 | 1.42e-14 |
| cantilever uniform load deflection | -40.2565985411 | -40.2565985411 | 7.11e-15 |
| axial extension | 0.0417972831766 | 0.0417972831766 | 0 |
| torsional rotation | 4.34782608696 | 4.34782608696 | 0 |
| simply supported exact midspan deflection | 43.5388366423 | 43.5388366423 | 7.11e-15 |

## Zgodność formuł Excel z niezależnym modelem

Dla wszystkich 6 przypadków w obu modelach porównano pełne macierze 36×36,
36 DOF przemieszczeń, 36 reakcji, 12 sił końcowych każdego pręta oraz globalną
równowagę sił i momentów. Odrębnie sprawdzono sumę obciążeń z pola powierzchni,
bez kopiowania formuł rozdziału obciążeń z generatora. Dla aktywnych kombinacji
porównano obwiednie momentów i ugięcia w 21 punktach/pręt.

| Grupa, baza | Maks. różnica bezwzględna |
|---|---|
| Przemieszczenia (mm/rad) | 1.56568e-11 |
| Reakcje (N/Nmm) | 1.97324e-07 |
| Siły końcowe (N/Nmm) | 1.97324e-07 |
| Macierz K (jednostki mieszane) | 3.33786e-06 |

Tolerancje są zapisane przy każdym teście w JSON. Porównania wykorzystują tolerancję
względną i bezwzględną; jednostki zależą od DOF. To nie jest deklaracja pokrycia
wszystkich mechanizmów zniszczenia.

## Wymagane scenariusze

| Scenariusz | Wykonanie i wynik |
|---|---|
| 1. Ściana prostokątna | baseline A; zgodność mechaniki i obciążeń — zaliczone |
| 2. Ściana trójkątna | triangle A, wysokości 0/1200/0, W=2400; zgodność modelu i aliasów — zaliczone |
| 3. Tylko w płaszczyźnie ściany | przypadek H w A — zaliczone |
| 4. Prostopadle do ściany | przypadek W+ w A — zaliczone |
| 5. Oba kierunki ściany | aktywne kombinacje w overload, współczynniki syntetyczne — zaliczone |
| 6. Wysuwnica ściana + wiązar | baseline B, indywidualne blokady — zaliczone |
| 7. Obciążenie pionowe | G/S w B — zaliczone |
| 8. Obciążenie poziome | H w B — zaliczone |
| 9. Oba kierunki wysuwnicy | aktywne kombinacje w overload — zaliczone |
| 10. Ssanie | W− w B, reakcje i równowaga z zachowaniem znaków — zaliczone |
| 11. Przekroczenie | overload: syntetyczne γ/ψ i obniżone fm/ft/fc; oba moduły NIE SPEŁNIA — zaliczone |
| 12. Brak danych | missing: pusta szerokość, brak aktywnego wyniku i brak błędów Excel — zaliczone |
| Mechanizm | wszystkie DOF swobodne, kontrola odwrotności blokuje wynik — zaliczone |
| Zmiana wejścia | changed_geometry: trapez, inne przekroje, kąt, obciążenie skupione — zaliczone |
| Serializacja | dostarczony XLSX zapisano, ponownie odczytano i porównano wyniki — zaliczone |
| Wykluczenie wiatrów | w żadnej kombinacji nie występują W+ i W− razem — zaliczone |

**Zaliczenie dotyczy powyższego modelu mechanicznego i kontroli technicznych.**
Nie oznacza wykonania normowej analizy przepony, kotew, łączników, wyboczenia,
zwichrzenia ani pełnej weryfikacji projektu ściany/wysuwnicy. Takie sprawdzenia
pozostają **niewykonane**. Współczynniki z pliku overload są wyłącznie syntetycznymi
danymi testowymi; nie trafiły jako normowe domyślne wejścia do dostarczanego XLSX.

## Raporty maszynowe

`tests/*-results.json` zawierają nazwy, wyniki, różnice i tolerancje.
`tests/summary.json` zestawia sześć wariantów. Liczby asercji numerycznych nie są
liczbą niezależnych przykładów projektowych. Plik dostarczany ma dodatkowy raport
`Kalkulator_konstrukcji_drewnianych-results.json`.

## Audyt arkusza i wydruku

- Brak błędów #REF!, #VALUE!, #DIV/0!, #N/A i innych komórek typu error w testowanych plikach.
- Brak makr VBA i odwołań do zewnętrznych skoroszytów.
- Formuły i cache wyników/wykresów zachowano w oryginalnym układzie XLSX.
- Karty DANE przejrzano na renderze PDF: białe karty, niebieskie wejścia, szare formuły, żółte ograniczenia.
- RAPORT wyeksportowano do dwóch stron A4; osobny PDF ma własną numerację.
- GitHub Actions przygotowano, lecz jego zdalnego przebiegu nie potwierdzono.
- Kontrole istniejącej aplikacji npm run check również zaliczone: lint, typy, 4 testy i build.

## Naprawione problemy techniczne

Zwykła konwersja LibreOffice zachowywała zerowe cache zamiast przeliczać wejścia.
Włączono OOXMLRecalcMode=Always i zweryfikowano rzeczywiste liczby, nie tylko brak
błędu procesu. Pobranie pakietów Calc wykonano z podpisanego repozytorium Debian;
zainstalowano je lokalnie bez podnoszenia uprawnień systemowych. Pełne macierze
zrównoważono diagonalnie, a osobny test odwrotności wykrywa mechanizmy.
Warianty parcia i ssania rozdzielono również dla oddziaływań towarzyszących.
Nie wyłączano weryfikacji TLS, podpisów pakietów ani kontroli wyników.
