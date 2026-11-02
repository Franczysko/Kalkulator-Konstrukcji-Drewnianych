# Model, równania i jednostki

## Zakres i jednostki

Liniowa sprężysta rama przestrzenna Eulera–Bernoulliego, pręty proste o stałym
prostokątnym przekroju i sztywno połączonych końcach. Geometria nominalna w mm,
siły N, momenty Nmm, kąty rad, E/G i naprężenia N/mm². Wejścia: kN, kNm,
kN/m i kN/m²; `1 kN/m = 1 N/mm`.

Model nie jest analizą przepony ani modelem płyty. Nie wolno utożsamiać sztywnego
węzła MES ze zwykłym kątownikiem lub płytką kolczastą bez odrębnego uzasadnienia.

## Geometria

Ściana: węzły 1–3 w podwalinie, 4–6 na oczepie. Słupki 1–4, 2–5, 3–6,
podwalina 1–2–3, oczep 4–5–6. Przy zerowej wysokości krawędzi odpowiedni słupek
jest nieaktywny, górny węzeł aliasowany w oczepie do narożnika dolnego, a nieaktywny
węzeł odłączony i zablokowany. Domyślne utwierdzenie stóp wymaga potwierdzenia
rzeczywistej sztywności podwaliny, kotew i podłoża.

Wysuwnica: dwa ciągi 1–2–3 i 4–5–6; trzy poprzeczki 1–4, 2–5, 3–6.
Stacje X = −a, 0, c. W jest rzeczywistą szerokością po połaci:
`Y=W cos α`, `Z=W sin α`. Ściana X=0, wiązar X=−a, okap X=c.
Podpory domyślnie blokują translacje 1/2/4/5, pozostawiając swobodę obrotów.
Wspornik blokuje sześć DOF 1 i 4; brak podpór 2 i 5.

Węzły wewnętrzne są sztywne we wszystkich wariantach. Zmiana blokad podpory nie
wprowadza przegubu między prętami.

## Przekrój i osie

`A=bh`, `Iy=bh³/12`, `Iz=hb³/12`, `Wy=Iy/(h/2)`, `Wz=Iz/(b/2)`.
Lokalna x: od i do j. Lokalna y: znormalizowane `Z_global × x`, a dla pręta
pionowego globalna X. Lokalna z = x × y. b jest wymiarem w lokalnej y, h w z.
Orientację prętów należy uwzględnić przy interpretacji przekrojów.

Dla skręcania Saint-Venanta prostokąta, a=max(b,h), d=min(b,h):

`J=a d³/3 · [1 − 192 d/(π⁵a) Σ tanh(nπa/(2d))/n⁵]`, n=1,3,…,49.

To wzór mechaniki, nie wzór nośności Eurokodu. Brak paczenia i kontroli τ od T.

## Metoda sztywności

DOF pręta: `[u,v,w,rx,ry,rz]i`, następnie analogiczne j.
Macierz lokalna zawiera EA/L, GJ/L oraz standardowe bloki zginania
12EI/L³, ±6EI/L², 4EI/L, 2EI/L. Transformacja T ma cztery bloki 3×3 R.

`k_global=Tᵀ k_local T`, `K=Σ assemble(k_global)`, `Ku=F`.

Wektor równoważny dla jednorodnego qx/qy/qz w osiach lokalnych:

- siły po qL/2 na końcu i i j;
- My,i=−qz L²/12, My,j=+qz L²/12;
- Mz,i=+qy L²/12, Mz,j=−qy L²/12.

Obciążenia globalne są transformowane przed utworzeniem wektora; po powrocie
do globalnego układu sumowane z siłami skupionymi. Reakcje `R=Ku−F` to działania
podpory na konstrukcję, więc działania na łącznik mają znak przeciwny.
Ujemne Rz przy podporze oznacza zapotrzebowanie na mocowanie przeciw unoszeniu.

MINVERSE obejmuje tylko macierz 36×36. Przed odwróceniem stosuje się normalizację
przez √Kii. Zablokowane DOF mają jednostkowy wiersz/kolumnę i zerowe obciążenie
w układzie rozwiązującym; macierz pierwotna pozostaje dostępna do reakcji.
Test `K_scaled · K_scaled_inverse ≈ I` wykrywa mechanizm lub problem numeryczny.
Wartości techniczne L≥1 mm/A≥1 mm² służą wyłącznie do uniknięcia błędów Excela
przy niekompletnych danych; nie są zastępczą geometrią i wyniki są blokowane.

## Odzyskanie sił i przemieszczeń

`f_local=k_local·T·u_global−f_equivalent`.
W przekroju x: N=−Fxi−qx x, My=−Myi−Fzi x−qz x²/2,
Mz=−Mzi+Fyi x+qy x²/2. Ekstrema momentów sprawdzane na końcach i w miejscach
zerowego ścinania x=−Fz/qz i x=−Fy/qy należących do [0,L].

Przemieszczenia poprzeczne: funkcje Hermite’a H1…H4 z dodatkowym dokładnym
rozwiązaniem szczególnym q·x²(L−x)²/(24EI). Ugięcie osiowe zawiera qx·x(L−x)/(2EA).
Wynik u to maksimum normy wektora w **21 punktach/pręt**, obejmuje ruch węzłów.
Nie jest dokładnym ekstremum ciągłym ani ugięciem względem cięciwy; brak podatności
złączy i odkształcenia postaciowego. Długie lub silnie zginane pręty wymagają
adekwatności teorii małych przemieszczeń.

## Pasma wpływu

Ściana: W/4, W/2, W/4 na trzech słupkach. Przy nierównych wysokościach suma
obciążenia odpowiada polu dwóch trapezów; nie dowodzi rzeczywistego rozkładu
z poszycia na słupki. G/S/Q działają pionowo, H w +X, W+/W− w ±Y.
G w modelu ściany jest wejściowym równoważnym pionowym obciążeniem na powierzchnię
modelowanej ściany. Reakcje z dachu należy wprowadzać jako rzeczywiste siły węzłowe,
a nie utożsamiać tego pola automatycznie z ciężarem pokrycia całego dachu.

Wysuwnica: pasma poprzeczek a/2, (a+c)/2, c/2. G/Q na powierzchnię połaci;
S na rzut poziomy (czynnik cos α); W netto prostopadle do połaci.
W+ = parcie w kierunku −normalna; W− = ssanie +normalna.
Dodatkowo w G uwzględniono ciężar każdego aktywnego pręta ρ·A·g.
Nie ma automatycznego wyznaczania cpe, cpi, μ, stref ani zaspy śnieżnej.

## Kontrole przekroju

PN-EN 1995-1-1:2010, pkt 2.4.1, (2.14): `Xd=kmod Xk/γM`.
Naprężenia N/A i M/W. Dla prostokąta km=0.7, pkt 6.1.6.
Kontrole z rozciąganiem: (6.17)/(6.18); ze ściskaniem: (6.19)/(6.20).
Współczynnika kh zwiększającego wytrzymałość nie użyto (kh=1).
Maksima N i My/Mz mogą pochodzić z różnych miejsc pręta, stąd konserwatywna
obwiednia zamiast jednego krytycznego przekroju. To nie jest sprawdzenie wyboczenia.
Nie wprowadzono redukcji kc/kcrit, kcr, otworów ani karbów.

γM=1.3 dla drewna litego: tab.2.3, NA.2 dostarczonego wydania.
kmod: tab.3.1, wybrany niezależnie dla każdej kombinacji po najkrótszym aktywnym
czasie. NA.1: śnieg średniotrwały; wiatr krótkotrwały. H i Q przyjęto jako
średniotrwałe — wymaga to sprawdzenia rzeczywistego charakteru oddziaływań.

## Kombinacje

K1…K6 są jednostkowymi przypadkami charakterystycznymi. U1…U18 to kandydaci
według formy 6.10: dwa γG, zmienne prowadzące oraz towarzyszące γQψ0, oddzielne
warianty W+ i W− oraz G-only. Parcie i ssanie nigdy nie działają razem.
Współczynniki wymagają wpisu i weryfikacji źródła PN-EN 1990/NA.
Nie jest to komplet wszystkich możliwych korzystnych/niekorzystnych podzbiorów
oddziaływań, 6.10a/b ani EQU, STR/GEO w sytuacjach szczególnych.

S1/S2: wyłącznie przykład SGU ze śniegiem prowadzącym i parciem towarzyszącym.
S2: uG·(1+kdef)+uS·(1+ψ2,S kdef)+uW+·(ψ0,W+ψ2,W kdef), wg 2.2.3,
(2.3)–(2.5) pierwszej generacji EC5. Brak pełnej obwiedni SGU.
Reakcje i siły S2 w tablicy to sprężyste siły od kombinacji; wzrost kdef stosuje
się do przemieszczeń, nie do reakcji.
