# Gable panel stud — adaptacja PL z zachowaniem wyglądu oryginału

Gotowy plik: [Gable_panel_stud_PL_v2.xlsx](../output/Gable_panel_stud_PL_v2.xlsx).

Poprawka zgodności z Microsoft Excel: usunięto nieaktualny `calcChain.xml` i jego
odwołania. Wcześniejszy plik zawierał dwa wpisy P60, które po adaptacji nie były
już formułami. Excel zgłaszał naprawę tych rekordów. Formuły, wartości i wygląd
pozostały bez zmian; automatyczne pełne przeliczenie pozwala Excelowi odtworzyć łańcuch.
Test odtwarza dokładny problem z opublikowanego pliku i sprawdza usunięcie tylko
metadanych: `python excel/gable_pl/test_package_fix.py`. Nie wykonano otwarcia
wersji v2 w desktopowym Microsoft Excel w tym środowisku Linux.

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
- **34 elementy identyczne bajt po bajcie**, w tym styles.xml, motyw, rysunki,
  VML, kontrolki, ustawienia drukarek, relacje i pozostałe pliki;
- identyczne metadane układu wszystkich trzech arkuszy: komórki i ich style,
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
potwierdzonym polskim materiałem**. Wybór TR26 nie daje wyniku OK.
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
uniwersalnego polskiego limitu dla słupka. Bez potwierdzenia nie daje wyniku OK.
Nie zastąpiono go arbitralnie L/300 dla belki, która nie jest tym słupkiem.

Nie wykazano rzeczywistego usztywnienia słupka, podparcia na obu końcach,
zabezpieczenia przed zwichrzeniem, nośności łączników i warunków stosowania
metody γ. Samo d=3,35 mm i s=300 mm z oryginału nie wystarcza do sprawdzenia
nośności i rozmieszczenia gwoździ. Wzór Kser przyjęto dla gwoździ bez nawiercania,
drewno–drewno, wg tab.7.1; nie dla dowolnych wkrętów, płytek lub kleju.

## Parametry bez dodawania pól do oryginalnego układu

Dodatkowe założenia są nazwami skoroszytu, dostępnymi w Excelu przez
**Formuły → Menedżer nazw**. Nie ma nowych arkuszy ani ukrytych tabel.

| Nazwa | Domyślnie | Znaczenie |
|---|---|---|
| `_PL_klasa_uzytkowania` | 2 | Klasa 1, 2 lub 3 |
| `_PL_Ce`, `_PL_Ct` | 1 | Współczynniki śniegu przyjęte przez projektanta |
| `_PL_beta_L` | 1 | Wspólny współczynnik długości wyboczeniowej; nie zmienia momentu i ugięcia belki |
| `_PL_ksys` | 1 | Brak automatycznego zwiększenia wytrzymałości za współpracę systemu |
| `_PL_limit_ratio` | 0,0045 | Przykładowy limit u/L odziedziczony z UK |
| `_PL_kombinacje_potwierdzone` | 0 | Nie potwierdzono kombinacji PN-EN 1990/NA |
| `_PL_wiatr_potwierdzony`, `_PL_snieg_potwierdzony` | 0 | Dane rzeczywistego obiektu wymagają potwierdzenia |
| `_PL_schemat_potwierdzony` | 0 | Brak potwierdzenia warunków podparcia i stateczności poza sprawdzonym mechanizmem |
| `_PL_limit_potwierdzony` | 0 | Brak uzasadnionego limitu SGU dla konkretnego projektu |
| `_PL_polaczenie_potwierdzone` | 0 | Brak kompletnego zewnętrznego sprawdzenia połączenia warstw |
| `_PL_Flacznika_Rd_N` | 0 | Brak potwierdzonej obliczeniowej nośności łącznika |

Wartość 1 dla potwierdzenia oznacza rzeczywiste udokumentowane sprawdzenie przez
projektanta, **nie sposób na ominięcie brakującej analizy**. Przy braku danych
przypadek bez przekroczenia daje NZ. FAIL oznacza przekroczenie dla aktualnie
wprowadzonych danych i założeń; OK może dotyczyć wyłącznie zakresu tej karty.
Żaden status nie zastępuje projektu całej ściany, przepony ani prefabrykatu.

## Wyniki przykładu po korektach

C24, klasa użytkowania 2, bez kredytowania niepotwierdzonych stężeń:

| Karta | Wykorzystanie | Ugięcie chwilowe |
|---|---:|---:|
| Flatwise timber | 1,4904 | 24,9079 mm |
| Edgewise timber | 2,0259 | 26,7746 mm |

Obie karty pokazują FAIL dla pozostawionych danych przykładowych i przyjętych
założeń. Nie oznacza to oceny rzeczywistej ściany z innymi przekrojami,
rozstawami, stężeniami lub obciążeniami. Ugięcie jest chwilowe od wiatru;
nie zaimplementowano pełzania, II rzędu i pełnej obwiedni SGU.

## Weryfikacja i odtworzenie

337 kontroli: niezależne wzory dla siły osiowej, momentu, kc, nośności,
ugięcia, sztywności zespolonej i obciążenia gwoździa; C18/C24/C30; klasa
użytkowania 3; nachylenia 30/45/60°; 1/2/3 warstwy; ssanie; inny rozstaw
słupków i odległość wiązara; zmiana długości wyboczeniowej; brak wiatru;
same obciążenia stałe; kontrola braku fałszywego OK. Do tego kontrola pakietu
i ponowne otwarcie pliku dostarczanego. Wyniki: [test_results.json](test_results.json).

```sh
python excel/gable_pl/adapt.py "Gable panel stud design EC5.xlsx" excel/output/Gable_panel_stud_PL.xlsx
LO_BIN=soffice python excel/gable_pl/test_adaptation.py "Gable panel stud design EC5.xlsx"
```

Wymagania: `excel/gable_pl/requirements.txt` (w tym lxml dla testu struktury XML) i LibreOffice
Calc do QA. **Dostarczany plik Excel nie wymaga Pythona ani LibreOffice.**
Oryginału i pełnych norm nie opublikowano; do odtworzenia należy użyć załącznika
użytkownika o sumie kontrolnej wskazanej w `provenance.json`.
