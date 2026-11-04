# Współczynniki ze zrzutu — które są prawidłowe?

Nie wszystkie są uniwersalnymi wartościami normowymi. Arkusz oblicza wyniki
z wpisanych danych, a OK dotyczy tylko pokazanej kontroli dla tych danych.

| Pozycja ze zrzutu | Ocena |
|---|---|
| cpe = 0,85 | Dane konkretnej powierzchni i kierunku; zależy m.in. od strefy ściany, proporcji budynku i obciążonej powierzchni. Nie potwierdzono go dla Twojego budynku. |
| cpi = −0,3 | Dane konkretnego przypadku ciśnienia wewnętrznego; zależy od otworów/przepuszczalności. Należy rozpatrzyć także drugi niekorzystny znak; nie jest stałą dla każdego budynku. |
| γM = 1,3 | Zgodne dla drewna litego w rozpatrywanym SGN według tab.2.3 przyjętej EC5/PL NA. |
| kmod = 0,9 | Zgodne przy aktywnym wietrze, klasie użytkowania 1 lub 2 i klasyfikacji wiatru jako krótkotrwałego według polskiego NA. Dla klasy 3 jest 0,7. |
| γG = 1,35; γQ = 1,5 | Typowe wartości dla odpowiedniej sytuacji i niekorzystnych oddziaływań, ale nie zastępują doboru kombinacji. Pełnej PN-EN 1990/PL NA nadal nie ma w materiałach. |
| ψ0 śniegu = 0,5 | Wymaga potwierdzenia dla przyjętej podstawy kombinacji i konkretnego przypadku. Arkusz sprawdza wiatr prowadzący, nie pełną obwiednię ze śniegiem prowadzącym. |
| fm,k = 24; fc,0,k = 21 MPa | Zgodne z C24 w przyjętej PN-EN 338:1999, tab.1. Trzeba rzeczywiście zastosować drewno odpowiedniej klasy. |
| Emean = 11000; E0,05 = 7400; G = 690 MPa | Zgodne z C24 w tej samej przyjętej tabeli. |
| kh = 1,27226 | Rachunkowo zgodne dla wysokości przekroju zginanego 45 mm: min((150/45)^0,2; 1,3), w zakresie warunków 3.2(3) dla drewna litego. Należy sprawdzić rzeczywistą orientację przekroju. |
| βc = 0,2 | Zgodne dla drewna litego wg 6.3.2, (6.29). |
| Le = 4000 mm | Założenie o schemacie i usztywnieniu, nie wartość materiałowa ani uniwersalna z normy. Wymaga potwierdzenia. |
| i = 12,99038 mm | Zgodne dla wymiaru 45 mm: 45/√12. |
| λ = 307,9201; λrel = 5,22134; k = 14,62333; kc = 0,035357 | Rachunkowo spójne z Le=4000 mm, i=45/√12 oraz fc,0,k=21 i E0,05=7400. Nie potwierdza to poprawności założonego Le. |
| ρ płyty MFP/OSB | Nie wynika z klasy C24 ani z samej grubości. Potrzebna jest karta konkretnego produktu. |

## Rachunek ze zrzutu

A=6525 mm², W=48937,5 mm³ i I=1101093,75 mm⁴ odpowiadają prostokątowi
145×45 mm przy zginaniu z wysokością 45 mm:

- A=145·45;
- W=145·45²/6;
- I=145·45³/12;
- i=45/√12;
- Mk=0,552·4000²/8=1 104 000 Nmm.

Pokazane q i moment są wielkościami charakterystycznymi; γQ jest nakładane
w dalszym obliczeniu naprężeń. Etykieta „des wp” pochodzi z oryginału i nie
powinna być interpretowana jako dowód wcześniejszego przemnożenia przez γQ.

Nie można na tej podstawie powiedzieć „wszystko jest poprawnie założone”.
Zweryfikowane są liczby materiałowe i zgodność rachunku. Do potwierdzenia pozostają
obciążenia konkretnego obiektu, kombinacje, podparcie, rzeczywiste usztywnienie
oraz połączenia. W szczególności samo wybranie MFP/OSB nie oznacza bocznego
podparcia słupka przez tę płytę.
