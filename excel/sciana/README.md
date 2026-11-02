# Ściana szczytowa — jeden formularz danych

Przebudowano **przesłany przez użytkownika `Sciana_Szczytowa_PL.xlsx`**, a nie starszy
skoroszyt z repozytorium.

Gotowy plik: [Sciana_Szczytowa_PL.xlsx](../output/Sciana_Szczytowa_PL.xlsx).

## Obsługa

Wszystkie podstawowe dane wpisuje się w **DANE WEJŚCIOWE**. Arkusz
**ŚCIANA SZCZYTOWA** jest tylko kartą schematu i wyników; szare pola pobierają dane
z formularza. Arkusze modelu, macierzy i poprzedniego formularza zachowano jako
ukryte. Wszystkie arkusze wysuwnicy i macierz B są ukryte; moduł odłożono na później.

Kolejność formularza:

1. Wiatr: źródło/Pamir, strefa, wysokość n.p.m., vb, teren, qp, cpe i cpi.
2. Śnieg: źródło/Pamir, strefa, sk, Ce, Ct, μ.
3. Obciążenia w układzie Pamira: stałe i zmienne pasa górnego, stałe pasa dolnego,
   stałe ściany, ciężar drewna — w N/m².
4. Budynek i ściana: szerokość, długość, poziom wieńca, poziom kalenicy, kolankowa.
5. Automatyczny schemat i wybór drewna / przekroju.
6. Opcjonalne reakcje wiązara z Pamira — grupa wierszy 98–134 do rozwinięcia.
7. Ręczne limity kontrolne.

## Cztery geometrie

| Wariant | Wysokości lewa / środek / prawa nad wieńcem |
|---|---|
| Szczytowa – trójkąt | 0 / H / 0 |
| Prostokąt | H / H / H |
| Szczytowa jednospadowa | 0 / H/2 / H |
| Szczytowa ze ścianką kolankową | hk / H / hk |

`H = poziom kalenicy − poziom wieńca`. To poziomy od **wspólnego zera** budynku,
nie grubość wieńca. Dla prostokąta poziom kalenicy jest poziomem górnej krawędzi.
Dla jednospadowej niska krawędź jest po lewej. Dla wariantu kolankowego hk musi
być większe od 0 i mniejsze od H.

Wykres rysuje odcinki proste, bez wygładzania. Pokazuje także dane z ukrytych
komórek pomocniczych. Zero na końcu trójkąta wyłącza zerowy słupek i aliasuje
oczep do dolnego narożnika; nie dodano fikcyjnego słupka 1 mm. Pomocnicza długość
1 mm występuje tylko w **nieaktywnym** elemencie o zerowej sztywności i obciążeniu.

## Skąd brać E, G i „p”?

„p” w starym widoku to **ρ — gęstość drewna**, nie parcie wiatru.

- E0,mean: średni moduł sprężystości wzdłuż włókien [MPa].
- Gmean: średni moduł ścinania [MPa]; nie mylić z obciążeniem stałym Gk.
- ρmean: średnia gęstość [kg/m³], używana do ciężaru własnego.

Po wyborze C18/C24/C30 wartości pobierają się z MATERIAŁY. Wprowadzono wyłącznie
sztywności i gęstości odczytane z dostarczonego **PN-EN 338:1999, tablica 1**.
To historyczne źródło, którego aktualności dla projektu nie potwierdzono. Nie
uznano przez to drewna w rzeczywistym prefabrykacie za zweryfikowaną klasę.
Dla danych własnych rozwiń wiersze 91–94 i podaj dane oraz źródło deklaracji/produktu.
E/G/ρ dotyczą wszystkich siedmiu prętów jednorodnego modelu, nie tylko słupków.

## Skąd brać parcie, ssanie i cpi?

**Tryb Pamir (netto):** przepisz gotowe wartości z raportu obciążeń dla właściwej
strefy ściany i kierunku wiatru. Parcie i bezwzględne ssanie podaje się jako
wartości dodatnie w N/m². Nie dodawaj do nich ponownie cpi lub qp. W tym trybie
qp/cpe/cpi mogą pozostać puste.

**Tryb qp i współczynniki:** wpisz qp(z), cpe dla parcia i ssania oraz **osobne**
cpi dla obu niekorzystnych przypadków. Arkusz liczy:

`w = qp · (cpe − cpi)`.

Źródła: PN-EN 1991-1-4, pkt 4.5 dla qp, 7.2.2 dla współczynników ścian, 7.2.9 dla
ciśnienia wewnętrznego, wraz z właściwym polskim NA. cpi zależy m.in. od otworów
i przepuszczalności; nie wpisano uniwersalnej wartości domyślnej. Przy danych
brakujących lub niewłaściwym znaku wynik nie jest zastępowany zerowym ciśnieniem.

Strefa, wysokość n.p.m., vb i teren **nie stanowią ukończonego generatora qp**.
Arkusz nie dobiera jeszcze map stref, profilu terenu, topografii, cpe ani cpi.
Wpisz wartości z raportu Pamira lub sprawdzonych obliczeń normowych.

Dla śniegu analogicznie: gotowe s z Pamira albo `s = μ · Ce · Ct · sk`.
Wysokość n.p.m. jest wspólna dla danych lokalizacji wiatru i śniegu. Zmiana strefy
lub wysokości nie zmienia automatycznie sk i qp. Należy rozpatrzyć właściwe układy
śniegu i kierunki wiatru, a nie tylko jedną parę współczynników.

## Obciążenia dachu a obciążenie ściany

PG/PD i śnieg są danymi projektu **dachu**. Nie są automatycznie obciążeniem
każdego słupka ściany. Zależnie od rzeczywistego schematu, dach może przekazywać
na ścianę reakcje lub nie opierać się na niej. Wprowadza się je w rozwijanej
tabeli reakcji. Siły działające na ścianę mają znak przeciwny do reakcji podpory
na wiązar, jeśli tak raportuje je Pamir. W tym modelu Y jest pionem, Z kierunkiem
prostopadłym do ściany; jednostki tabeli to kN i kNm.

Automatyczny rozdział wiatru zachowuje sumę obciążenia powierzchniowego dla
czterech geometrii. Jest uproszczonym rozdziałem na trzy słupki, **nie analizą
poszycia ani zweryfikowanym modelem przekazywania sił przez przeponę**.

## Weryfikacja i ograniczenia

Wykonano 243 zapisane kontrole dla czterech kształtów, zmiany klasy na C18,
obliczania wiatru/śniegu, braku szerokości oraz ponownego otwarcia dostarczanego
pliku. Porównano wszystkie 36 przemieszczeń, 36 reakcji i macierz 36×36 dla każdego
z sześciu przypadków z niezależnym solverem NumPy. Sprawdzono równowagę sił i
momentów oraz sumę wiatru z pola ściany. Wyniki: [wyniki_testow.json](wyniki_testow.json).
Podglądy czterech kształtów wyrenderowano w LibreOffice. Wcześniejszy zestaw
regresji `python excel/tests/run.py` również przeszedł.

Nadal brak pełnej weryfikacji normowej, stateczności, połączeń i poszycia; wynik
ogólny pozostaje NIEZWERYFIKOWANE. Model ma tylko trzy słupki i siedem prętów.
Nie jest to pełny model ściany z dowolnym rozstawem słupków. Kontrola naprężeń
pozostaje kontrolą końców prętów. Nie uruchamiano Microsoft Excel 365 w tej sesji;
pliki faktycznie przeliczono w LibreOffice Calc 25.2.3.2 i ponownie odczytano.

## Odtworzenie

Plik źródłowy użytkownika pozostaje załącznikiem rozmowy i nie został dodatkowo
opublikowany. Modyfikator przyjmuje go jako argument:

```sh
python excel/sciana/przebuduj.py Sciana_Szczytowa_PL_oryginal.xlsx excel/output/Sciana_Szczytowa_PL.xlsx
python excel/sciana/test_przebudowa.py
```

Testy wymagają LibreOffice i zależności `excel/requirements.txt`. Opcjonalny eksport
podglądów wymaga również `excel/requirements-preview.txt`:

```sh
python excel/sciana/podglad.py excel/output/Sciana_Szczytowa_PL.xlsx excel/sciana/podglady dane_i_trojkat
```

## Podglądy czterech schematów

[Trójkąt](podglady/trojkat.png) · [Prostokąt](podglady/prostokat.png) · [Jednospadowa](podglady/jednospadowa.png) · [Ze ścianką kolankową](podglady/kolankowa.png)
