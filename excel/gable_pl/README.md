# Gable panel stud — adaptacja PL z zachowaniem wyglądu oryginału

Ocena współczynników: [WSPOLCZYNNIKI.md](WSPOLCZYNNIKI.md).

Gotowy plik: [Gable_panel_stud_PL_v3.xlsx](../output/Gable_panel_stud_PL_v3.xlsx).

Poprawka zgodności z Microsoft Excel: usunięto nieaktualny `calcChain.xml` i jego
odwołania. Wcześniejszy plik zawierał dwa wpisy P60, które po adaptacji nie były
już formułami. Excel zgłaszał naprawę tych rekordów. Formuły, wartości i wygląd
pozostały bez zmian; automatyczne pełne przeliczenie pozwala Excelowi odtworzyć łańcuch.
Test odtwarza dokładny problem z opublikowanego pliku i sprawdza usunięcie tylko
metadanych: `python excel/gable_pl/test_package_fix.py`. Nie wykonano otwarcia
wersji v3 w desktopowym Microsoft Excel w tym środowisku Linux.

Zgodnie ze zmianą planu jest to adaptacja **oryginalnego „Gable panel stud design
EC5.xlsx”**. Nie wykorzystuje przebudowanego wcześniej formularza ściany.
Nie dodano arkuszy, wierszy, kolumn, rysunków ani nowych pól na kartach. Zachowano
angielskie podpisy; zmieniono jedynie kilka istniejących uwag niezbędnych do
prawidłowej interpretacji wyników. Nie przeniesiono tu modelu całej ściany 3D.

## Zachowanie wyglądu

Plik modyfikuje się bezpośrednio w OOXML, bez zapisywania go przez OpenPyXL lub
LibreOffice. Silnik Calc służy wyłącznie do niezależnego przeliczenia kopii;
wyniki podręczne wracają do oryginalnych komórek bez zmiany ich formatowania.

Test wykazał:

- 40 elementów pakietu XLSX; usunięto wyłącznie opcjonalny, nieaktualny łańcuch obliczeń z oryginalnych 41 elementów;
- **30 elementów identycznych bajt po bajcie**, w tym styles.xml, motyw, rysunki,
  ustawienia drukarek i pozostałe pliki; w VML i właściwościach kontrolek zmieniono tylko zakres listy płyt z 9 na 11 pozycji;
- identyczne metadane układu obu kart obliczeniowych i dotychczasowych komórek bazy; w istniejących pustych wierszach bazy dodano dane dwóch płyt:
  wysokości/szerokości, scalenia, widoki, obszary wydruku i formatowanie warunkowe;
- zmiany wyłącznie zawartości komórek trzech arkuszy oraz metadanych przeliczania
  i parametrów nazwanych w workbook.xml; deklaracje pakietu i relacje zaktualizowano wyłącznie w celu usunięcia calcChain.xml.

Oczywiście liczby, wyniki i kilka opisów są inne — to cel adaptacji obliczeń.
Porównanie PDF oryginału i wersji PL dało tę samą liczbę pięciu stron i te same
rozmiary stron. Właściwy układ Excel zachowują oryginalne elementy pakietu.
Nie wykonano uruchomienia w Microsoft Excel; przeliczenia i PDF wykonano w
LibreOfficeDev 26.8.0.0.alpha0 oraz porównano z niezależną implementacją numeryczną.

## Normy: co jest dostępne

Zgodnie z poleceniem użytkownika **przyjęto dostarczone normy śniegowe i wiatrowe
jako podstawę zadania, bez aktualizowania ich wydań i poprawek**.

| Źródło | Stan i wykorzystanie |
|---|---|
| PN-EN 1995-1-1:2010 | Dostarczono, wraz z NA na stronach PDF 2–3; wykorzystano EC5 i polskie postanowienia |
| PN-EN 338:1999 / EN 338:1995 | Dostarczono; tab.1, str.7: klasy C14–C40, ich wytrzymałości, E, E0,05, G i gęstości |
| PN-EN 1991-1-3:2005 | Dostarczono; przyjęta podstawa śniegu; wejściowe sk w H14/H13 określa użytkownik |
| PN-EN 1991-1-4 | Dostarczony skan przyjęty zgodnie z poleceniem; qp, cpe, cpi pozostają wejściami konkretnego przypadku |
| PN-EN 1991-1-1:2004 | Dostarczono; ciężary pokrycia i ściany pozostają wejściami projektu |
| PN-EN 1990 + polski NA | **Pełnego źródła nie znaleziono w załącznikach**; poradnik zawiera fragmenty, niewystarczające do certyfikacji kombinacji |
| PN-EN 1995-1-2:2008, AC:2009; PN-EN 1194:2000 | Są w materiałach; nie są stosowane w tym sprawdzeniu drewna litego bez pożaru |
| PN-EN 14250 / EN 14592 | Brak pełnych norm w załącznikach; nie zadeklarowano weryfikacji produkcji prefabrykatu ani nośności konkretnego gwoździa |
| Deklaracje i ETA z archiwów | Dostępne; nie wyprowadzono z nich uniwersalnej nośności gwoździa 3,35 mm z przykładu |

Nie mieszano danych TR26 z klasą C24. Domyślnie wybrano istniejącą pozycję C24
(`Value!M6=2`); właściwości TR26 pozostawione w oryginalnej tabeli **nie są
potwierdzonym polskim materiałem**. Wybór TR26 daje FAIL jako nieobsługiwany materiał, nie jako udowodnione przekroczenie jego nośności.
Starsze wydanie PN-EN 338 zastosowano świadomie, zgodnie z poleceniem. Nie
zastąpiono go arbitralnie danymi z nowszego wydania.

## Wprowadzone korekty

1. **kmod:** PN-EN 1995-1-1:2010, NA.1 i tab.3.1. Dla klasy użytkowania 2:
   wiatr aktywny → 0,9, śnieg bez wiatru → 0,8, same stałe → 0,6.
   Dla klasy 3: odpowiednio 0,7 / 0,65 / 0,5. Nie pozostaje 1,1 z założenia UK.
2. γM=1,3 dla drewna litego: EC5 tab.2.3 / NA.2. Usunięto nieudokumentowane
   dodatkowe mnożenie wytrzymałości przez 1,1; ksys domyślnie 1,0.
3. **Wyboczenie:** poprawiono znak pod pierwiastkiem na `k²−λrel²`, wg
   6.3.2, (6.25)–(6.28). Przy λrel≤0,3 kc=1. Bez dowodu usztywnienia przyjęto
   konserwatywnie smukłość pojedynczej gałęzi względem słabszej osi.
4. Długość wyboczeniowa domyślnie L, zamiast nieuzasadnionego 0,85L.
   To model podparcia na obu końcach, a nie dowolnego wspornika.
5. **N od dachu:** obciążenia liniowe O44/O45 i O45/O46 [kN/m] mnożone są
   przez rozstaw słupków [m], zanim zostaną przeliczone na siłę i naprężenie.
6. Edgewise: poprawiono odwołanie w O46 z H16 na H15 (odległość pierwszego wiązara).
7. Śnieg: `s=μ1 Ce Ct sk`, μ1=0,8 do 30°, liniowo do 0 przy 60°.
   Usunięto minimum 0,6 kN/m² z oryginału. Ce=Ct=1 są jawnymi założeniami wejściowymi,
   nie automatycznie ustalonymi parametrami każdej lokalizacji.
8. **Ugięcie i moment:** używają rzeczywistej rozpiętości, nie długości
   wyboczeniowej. Ugięcie zawiera zginanie oraz ścinanie prostokąta (κ=5/6),
   przy G z tabeli materiałowej, zamiast przybliżenia E/16.
9. Moduły G i gęstości są związane z wybraną klasą. Gęstość Edgewise nie jest
   na stałe równa 450 kg/m³ po zmianie klasy z TR26 na C24.
10. **Annex B:** Kser dla SGU i Ku=(2/3)Kser dla SGN, wg 2.2.2(2), (2.1),
    tab.7.1 i B.2. Poprawiono γ3, składnik trzeciej warstwy i położenie osi.
    Dla SGU stosuje się oddzielne EI wyznaczone z Kser.
11. W Edgewise naprężenia osiowe warstw od zginania zespolonego nie są porównywane
    wyłącznie z fm,d. Kontrola uwzględnia fc,d i ft,d oraz lokalne zginanie;
    obwiednia jest konserwatywna dla jednakowych warstw.
12. Parcie i ssanie o przeciwnym znaku nie prowadzą do ujemnego „wykorzystania”
    lub ugięcia, które mogłoby dać fałszywe OK.

## Dane, które nadal określa projektant

Wartości qp=0,6 kN/m², sk=0,48 kN/m², cpe=0,85 i cpi=−0,3 pozostawiono jako
**przykładowe wejścia oryginału**, nie jako polskie wartości normowe dla dowolnej
lokalizacji. Należy je zastąpić danymi konkretnego obiektu. Arkusz nie wyznacza
stref geograficznych ani qp z wysokości/terenu.

γG=1,35, γQ=1,5, ψ0,s=0,5 pozostają widocznymi wejściami z oryginału. Nie uznano
ich za potwierdzony pełny polski zestaw kombinacji. W szczególności nie ma pełnej
obwiedni 6.10a/b, śniegu prowadzącego ani innych sytuacji projektowych.

0,0045L zachowano jako **odziedziczony limit projektowy**, aby nie wymyślać
uniwersalnego polskiego limitu dla słupka. Wynik OK dotyczy porównania z tym wpisanym limitem, którego zasadność trzeba sprawdzić dla projektu.
Nie zastąpiono go arbitralnie L/300 dla belki, która nie jest tym słupkiem.

Nie wykazano rzeczywistego usztywnienia słupka, podparcia na obu końcach,
zabezpieczenia przed zwichrzeniem, nośności łączników i warunków stosowania
metody γ. Samo d=3,35 mm i s=300 mm z oryginału nie wystarcza do sprawdzenia
nośności i rozmieszczenia gwoździ. Wzór Kser przyjęto dla gwoździ bez nawiercania,
drewno–drewno, wg tab.7.1; nie dla dowolnych wkrętów, płytek lub kleju.

## OK i FAIL — zakres wyniku

Usunięto status NZ i niewidoczne przełączniki potwierdzeń. Każde pole statusu
pokazuje wyłącznie **OK** albo **FAIL**:

- OK przy `csi`: policzony warunek przekroju i wyboczenia dla pokazanej kombinacji
  mieści się w granicy 1 przy poprawnych wejściach.
- OK przy ugięciu: policzone ugięcie mieści się we wpisanym limicie.
- FAIL: przekroczenie albo brak/błąd danych potrzebnych do danego sprawdzenia.
  Przy niekompletnych liczbach pola obliczeniowe mogą pokazywać BRAK.

To **nie jest zbiorcze zatwierdzenie projektu**, potwierdzenie wartości cpe/cpi,
pełnej obwiedni kombinacji ani nośności połączeń. Ten zakres podano w istniejących
uwagach obu kart; nie dodano pól ani przełączników akceptacji na kartach.

Parametry rzeczywiście uczestniczące w obliczeniach, dostępne przez Menedżer nazw:

| Nazwa | Domyślnie | Znaczenie |
|---|---|---|
| `_PL_klasa_uzytkowania` | 2 | Klasa 1, 2 lub 3 |
| `_PL_Ce`, `_PL_Ct` | 1 | Współczynniki śniegu przyjmowane dla obiektu |
| `_PL_beta_L` | 1 | Wspólny współczynnik długości wyboczeniowej; nie zmienia momentu i ugięcia |
| `_PL_ksys` | 1 | Brak automatycznego zwiększenia wytrzymałości za współpracę systemu |
| `_PL_limit_ratio` | 0,0045 | Odziedziczony limit projektowy u/L; nie uniwersalny polski limit |
| `_PL_G_inne_kN_m2` | 0 | Dodatkowy ciężar ściany dla dwóch nowych opcji płyt |

## MFP 12 mm i OSB 18 mm bez płyt g-k

W obu oryginalnych listach rozwijanych dostępne są dwie nowe pozycje:

- **EXTERNAL 12mm MFP, no insulation, no plasterboard** — pozycja 10;
- **EXTERNAL 18mm OSB, no insulation, no plasterboard** — pozycja 11.

Zachowano wielkość i położenie list. Zmieniono zakres zarówno w ctrlProps, jak
i w VML, aby natywny Excel widział obie opcje. Obie karty korzystają teraz
z wybranej płyty; pole F22 na Edgewise nie ma już stałej wartości 0,24.

Nie ma dostarczonej gęstości konkretnego produktu MFP/OSB. **Nie wpisano 700 kg/m³
ani innej hipotetycznej gęstości jako danych produktu.** W bazie Value wpisz:

| Komórka | Dane |
|---|---|
| U14 | Gęstość MFP 12 mm [kg/m³], z karty producenta |
| U15 | Gęstość OSB 18 mm [kg/m³], z karty producenta |

To gęstość **płyty**, nie gęstość drewna C24 wynosząca w przyjętej tabeli 420 kg/m³.
Dla nowych opcji masa jest liczona jako `g_płyty = ρ · t · 9,80665 / 1000 [kN/m²]`.
Każda karta dodaje ciężar własnego słupka, zależny od n·b·h, rozstawu i ρmean
wybranej klasy drewna, oraz ewentualne `_PL_G_inne_kN_m2`. Dotyczy jednej warstwy
poszycia. Ciężar drugiej strony, rygli, ocieplenia i innych warstw wymaga uzupełnienia.

Dotychczasowe 9 pozycji zachowuje dotychczasowe wartości ciężaru z szablonu.
Nie dołożono do nich automatycznie ponownie ciężaru słupków. Nie stwierdzono,
że te odziedziczone wartości są właściwe dla każdego rzeczywistego układu warstw.

Wybór płyty zmienia ciężar; **nie włącza automatycznie stężenia, sztywności przepony
ani skrócenia długości wyboczeniowej**. Takie działanie wymaga osobnej analizy
płyty, jej mocowania i przekazywania sił.

## Wyniki przykładu po korektach

C24, klasa użytkowania 2, bez kredytowania niepotwierdzonych stężeń:

| Karta | Wykorzystanie | Ugięcie chwilowe |
|---|---:|---:|
| Flatwise timber | 1,4904 | 24,9079 mm |
| Edgewise timber | 1,9675 | 26,7746 mm |

Obie karty pokazują FAIL dla pozostawionych danych przykładowych i przyjętych
założeń. Nie oznacza to oceny rzeczywistej ściany z innymi przekrojami,
rozstawami, stężeniami lub obciążeniami. Ugięcie jest chwilowe od wiatru;
nie zaimplementowano pełzania, II rzędu i pełnej obwiedni SGU.

## Weryfikacja i odtworzenie

394 kontrole: niezależne wzory dla siły osiowej, momentu, kc, nośności,
ugięcia, sztywności zespolonej i obciążenia gwoździa; C18/C24/C30; klasa
użytkowania 3; nachylenia 30/45/60°; 1/2/3 warstwy; ssanie; inny rozstaw
słupków i odległość wiązara; zmiana długości wyboczeniowej; brak wiatru;
same obciążenia stałe; kontrola statusów OK/FAIL, dwóch nowych płyt oraz FAIL przy braku gęstości. Gęstość 700 kg/m³ w testach jest wyłącznie wartością syntetyczną, nie danymi produktu. Do tego kontrola pakietu
i ponowne otwarcie pliku dostarczanego. Wyniki: [test_results.json](test_results.json).

```sh
python excel/gable_pl/adapt.py "Gable panel stud design EC5.xlsx" excel/output/Gable_panel_stud_PL.xlsx
LO_BIN=soffice python excel/gable_pl/test_adaptation.py "Gable panel stud design EC5.xlsx"
```

Wymagania: `excel/gable_pl/requirements.txt` (w tym lxml dla testu struktury XML) i LibreOffice
Calc do QA. **Dostarczany plik Excel nie wymaga Pythona ani LibreOffice.**
Oryginału i pełnych norm nie opublikowano; do odtworzenia należy użyć załącznika
użytkownika o sumie kontrolnej wskazanej w `provenance.json`.
