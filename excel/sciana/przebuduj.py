"""Przebudowa pliku użytkownika. Użycie: python przebuduj.py źródło.xlsx wynik.xlsx."""
from copy import copy
from pathlib import Path
import sys
from openpyxl import load_workbook
from openpyxl.chart import ScatterChart, Series, Reference
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, Protection
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.workbook.properties import CalcProperties
from openpyxl.utils import get_column_letter as C

BLUE='D9E8F7';GRAY='EEF0F2';YELLOW='FFF2CC';INK='24384A'
SHAPES=['Szczytowa – trójkąt','Prostokąt','Szczytowa jednospadowa','Szczytowa ze ścianką kolankową']

def rebuild(source,output):
 w=load_workbook(source); old=w['DANE WEJŚCIOWE']; old.title='_ARCHIWUM DANYCH'
 for s in w:
  for row in s:
   for c in row:
    if c.data_type=='f' and isinstance(c.value,str):c.value=c.value.replace("'DANE WEJŚCIOWE'!","'_ARCHIWUM DANYCH'!")
    elif hasattr(c.value,'text'):c.value.text=c.value.text.replace("'DANE WEJŚCIOWE'!","'_ARCHIWUM DANYCH'!")
 s=w.create_sheet('DANE WEJŚCIOWE',0);s.sheet_view.showGridLines=False;s.freeze_panes='F7'
 s.column_dimensions['A'].width=3
 for cc in range(2,6):s.column_dimensions[C(cc)].width=11
 for cc in [6,7]:s.column_dimensions[C(cc)].width=12
 s.column_dimensions['H'].width=10
 for cc in range(9,16):s.column_dimensions[C(cc)].width=10
 thin=Side(style='thin',color='BAC7D0')
 def merge(row,a,b,text,fill=None,bold=False,size=10):
  s.merge_cells(start_row=row,start_column=a,end_row=row,end_column=b)
  c=s.cell(row,a,text);c.font=Font(name='Calibri',size=size,bold=bold,color=INK);c.alignment=Alignment(vertical='center',wrap_text=True)
  if fill:c.fill=PatternFill('solid',fgColor=fill)
  return c
 def section(row,text):merge(row,2,15,text,GRAY,True);s.row_dimensions[row].height=25
 def field(row,label,value=None,unit='',note='',formula=False):
  merge(row,2,5,label)
  c=merge(row,6,7,value,GRAY if formula else BLUE);c.border=Border(bottom=thin,left=thin,right=thin,top=thin);c.number_format='0.###';c.protection=Protection(locked=formula)
  s.cell(row,8,unit).font=Font(name='Calibri',size=9,color='556677')
  merge(row,9,15,note,size=9);s.row_dimensions[row].height=29
  if note:c.comment=Comment(note,'Instrukcja')
 def listval(addr,items):
  dv=DataValidation(type='list',formula1='"'+','.join(items)+'"');dv.errorTitle='Wybierz pozycję z listy';dv.error='Nieznana opcja.';dv.showErrorMessage=True;s.add_data_validation(dv);dv.add(addr)
 def numval(addr,low=0,high=100000):
  dv=DataValidation(type='decimal',operator='between',formula1=str(low),formula2=str(high),allow_blank=True);dv.showErrorMessage=True;dv.error='Wprowadź liczbę w podanym zakresie.';s.add_data_validation(dv);dv.add(addr)
 merge(1,2,15,'DANE WEJŚCIOWE — ŚCIANA SZCZYTOWA',bold=True,size=17);s.row_dimensions[1].height=34
 merge(3,2,15,'Wszystkie dane wpisuj tutaj. Niebieskie = wejścia; szare = wyniki. ŚCIANA SZCZYTOWA służy wyłącznie do podglądu schematu i wyników.',YELLOW);s.row_dimensions[3].height=33
 field(4,'Projekt / inwestycja',None,'','Nazwa używana na karcie ściany; wpisywana tylko tutaj.')
 section(5,'01  OBCIĄŻENIE WIATREM — PN-EN 1991-1-4 / POLSKI NA / WYNIKI PAMIRA')
 fields=[
 (7,'Sposób podania wiatru','Pamir (netto)','','Pamir: przepisz parcie i ssanie netto; pola qp/cpe/cpi mogą zostać puste. Drugi tryb używa qp i współczynników.'),
 (8,'Podstawa / wydanie','PN-EN 1991-1-4 + polski NA','','Wpisz spójne wydanie normy i NA z raportu projektu. Aktualność nie jest potwierdzana przez arkusz.'),
 (9,'Strefa wiatrowa',1,'','Strefa z mapy polskiego NA / raportu Pamira. Sama zmiana strefy nie wyznacza qp.'),
 (10,'Wysokość nad poziomem morza',300,'m n.p.m.','Wysokość terenu, nie wysokość budynku. Uwzględnij ją przy doborze vb/sk zgodnie z właściwym polskim NA.'),
 (11,'Bazowa prędkość vb',22,'m/s','Wartość z raportu obciążeń / właściwego polskiego NA; nie jest tu przeliczana ze strefy.'),
 (12,'Kategoria terenu','I – teren otwarty','','Z raportu obciążeń. Wpływa na profil prędkości i qp; nie zastępuje wyznaczenia qp(z).'),
 (13,'Szczytowe ciśnienie qp(z)',785,'N/m²','Z raportu Pamira lub obliczeń PN-EN 1991-1-4, pkt 4.5. qp to ciśnienie prędkości, nie parcie netto ściany.'),
 (14,'cpe — przypadek parcia',None,'—','Współczynnik zewnętrzny dla konkretnej strefy ściany, kierunku wiatru i obciążonej powierzchni; EC1 7.2.2.'),
 (15,'cpe — przypadek ssania',None,'—','Wpisz ze znakiem. Ssanie zewnętrzne zwykle ma znak ujemny; źródło: raport / właściwy punkt normy.'),
 (16,'cpi — przypadek parcia',None,'—','Ciśnienie wewnętrzne, EC1 7.2.9: otwory i przepuszczalność budynku. Dla parcia wybierz niekorzystny przypadek z raportu.'),
 (17,'cpi — przypadek ssania',None,'—','Osobny przypadek cpi ze znakiem. Nie zakładaj tej samej wartości co dla parcia bez uzasadnienia.'),
 (18,'Pamir: parcie netto',500,'N/m²','Dodatnia wartość wynikowa NA ŚCIANĘ. Nie dodawaj do niej drugi raz qp ani cpi.'),
 (19,'Pamir: ssanie netto',700,'N/m²','Dodatnia wartość bezwzględna. W modelu działa w kierunku przeciwnym do parcia.'),
 (20,'Źródło / kierunek / strefa ściany',None,'','Wpisz numer raportu Pamira lub punkt normy, strefę powierzchni, kierunek wiatru i wysokość odniesienia z.'),
 ]
 for args in fields:field(*args)
 field(21,'Parcie przekazane do modelu','=IFERROR(IF(F7="Pamir (netto)",IF(AND(ISNUMBER(F18),F18>=0),F18,""),IF(AND(COUNT(F13,F14,F16)=3,F13>=0,F14-F16>=0),F13*(F14-F16),"")),"")','N/m²','Z qp: w = qp·(cpe−cpi). W trybie Pamir wynik jest już netto.',True)
 field(22,'Ssanie przekazane do modelu','=IFERROR(IF(F7="Pamir (netto)",IF(AND(ISNUMBER(F19),F19>=0),F19,""),IF(AND(COUNT(F13,F15,F17)=3,F13>=0,F15-F17<=0),-F13*(F15-F17),"")),"")','N/m²','Wartość bezwzględna; przypadek W− ma przeciwny znak obciążenia.',True)
 listval('F7',['Pamir (netto)','qp i współczynniki']);listval('F9',['1','2','3']);listval('F12',['0 – morze','I – teren otwarty','II – niska roślinność','III – zabudowa','IV – gęsta zabudowa'])
 for addr in ['F14','F15','F16','F17']:numval(addr,-5,5)
 section(25,'02  OBCIĄŻENIE ŚNIEGIEM — PN-EN 1991-1-3 / POLSKI NA')
 for args in [(27,'Sposób podania śniegu','Pamir','','Pamir: podaj gotowe obciążenie na rzut poziomy. Drugi tryb: s = μ·Ce·Ct·sk.'),(28,'Podstawa / wydanie','PN-EN 1991-1-3 + polski NA','','Właściwe wydanie i układy obciążenia określ w raporcie projektu.'),(29,'Strefa śniegowa',2,'','Z mapy właściwego polskiego NA. Strefa i wysokość n.p.m. służą do ustalenia sk poza tym arkuszem.'),(30,'Śnieg na gruncie sk',900,'N/m²','Z Pamira / właściwego polskiego NA, z uwzględnieniem wysokości terenu F10.'),(31,'Współczynnik ekspozycji Ce',1,'—','Dobierz według przyjętej normy i warunków terenu.'),(32,'Współczynnik termiczny Ct',1,'—','Dobierz według przyjętej normy i warunków cieplnych dachu.'),(33,'Współczynnik kształtu μ',None,'—','Z właściwego punktu normy dla geometrii dachu i układu śniegu; bez automatycznego doboru.'),(34,'Pamir: śnieg na dachu',800,'N/m²','Na rzut poziomy dachu. Do ściany przekazuj odpowiednie REAKCJE dachu, nie to ciśnienie bezpośrednio.')]:field(*args)
 field(35,'Śnieg przyjęty do projektu','=IFERROR(IF(F27="Pamir",IF(AND(ISNUMBER(F34),F34>=0),F34,""),IF(AND(COUNT(F30:F33)=4,MIN(F30:F33)>=0),PRODUCT(F30:F33),"")),"")','N/m²','Wartość do zestawienia dachu. Nie jest automatycznym obciążeniem powierzchniowym pionowej ściany.',True)
 field(36,'Źródło / układ śniegu',None,'','Numer raportu, układ równomierny/nierównomierny, zaspy i inne wymagane przypadki.');listval('F27',['Pamir','μ·Ce·Ct·sk']);listval('F29',['1','2','3','4','5'])
 section(38,'03  OBCIĄŻENIA JAK W PAMIRZE — WARTOŚCI CHARAKTERYSTYCZNE')
 for args in [(40,'Pas górny — stałe Gk',690,'N/m²','Zestawienie warstw dachu / raport Pamira; powierzchnia odniesienia musi być zgodna z raportem.'),(41,'Pas górny — zmienne Qk',500,'N/m²','Oddzielnie od śniegu. Rodzaj, kategorię i powierzchnię odniesienia przyjmij z raportu Pamira.'),(42,'Pas dolny — stałe Gk',300,'N/m²','Warstwy sufitu i pasa dolnego. Bez automatycznego przypisywania całej tej wartości każdemu słupkowi.'),(43,'Ściana — stałe Gk',300,'N/m²','Działa na ścianę; dodawane są zachowane warstwy okładzin z pliku źródłowego.'),(44,'Dodaj ciężar własny drewna','Tak','','Tak: ciężar prętów liczony z gęstości ρ i rzeczywistych przekrojów. Nie doliczaj go ponownie w Gk.')]:field(*args)
 listval('F44',['Tak','Nie'])
 merge(45,2,15,'PG/PD i śnieg są danymi projektu dachu. Do obliczeń ściany wprowadź reakcje wiązara poniżej. Samo ciśnienie na dach nie określa reakcji bez schematu wiązara i powierzchni wpływu.',YELLOW);s.row_dimensions[45].height=36
 section(47,'04  GEOMETRIA — POZIOMY BUDYNKU I KSZTAŁT ŚCIANY')
 for args in [(49,'Rodzaj ściany',SHAPES[0],'','Cztery warianty; schemat i wysokości słupków zmieniają się automatycznie.'),(50,'Szerokość budynku / ściany',8000,'mm','Szerokość modelowanej ściany szczytowej.'),(51,'Długość budynku',16000,'mm','Dane do raportu obciążeń wiatrem i dachu; nie jest rozpiętością ściany.'),(52,'Poziom górnej powierzchni wieńca',4000,'mm','Poziom od wspólnego zera budynku, nie grubość wieńca.'),(53,'Poziom kalenicy / górnej krawędzi',7000,'mm','Od tego samego zera co wieniec. Dla prostokąta: poziom górnej krawędzi ściany.'),(54,'Wysokość ścianki kolankowej',0,'mm','Używana tylko dla wariantu „ze ścianką kolankową”; liczona ponad wieńcem.')]:field(*args)
 listval('F49',SHAPES)
 field(55,'Wysokość ściany nad wieńcem','=IF(COUNT(F52:F53)=2,F53-F52,"")','mm','Poziom kalenicy / górnej krawędzi minus poziom wieńca.',True)
 field(56,'Wysokość lewego słupka','=IF(F49="Prostokąt",F55,IF(F49="Szczytowa ze ścianką kolankową",F54,0))','mm','Wysokości dotyczą modelu ponad wieńcem.',True)
 field(57,'Wysokość środkowego słupka','=IF(F49="Szczytowa jednospadowa",F55/2,F55)','mm','Dach symetryczny ma kalenicę pośrodku. Jednospadowy: lewa krawędź niska, prawa wysoka.',True)
 field(58,'Wysokość prawego słupka','=IF(OR(F49="Prostokąt",F49="Szczytowa jednospadowa"),F55,IF(F49="Szczytowa ze ścianką kolankową",F54,0))','mm','Trójkąt zwykły ma skrajne wysokości 0; nie jest rysowany jako prostokąt.',True)
 field(59,'Kąt połaci / górnej krawędzi','=IFERROR(IF(F49="Prostokąt",0,DEGREES(ATAN((F55-F56)/IF(F49="Szczytowa jednospadowa",F50,F50/2)))),"")','°','Kąt wynikowy; dla prostokąta 0°.',True)
 field(60,'Kontrola geometrii','=IFERROR(IF(AND(COUNT(F50:F54)=5,F50>0,F51>0,F55>0,F54>=0,IF(F49="Szczytowa ze ścianką kolankową",AND(F54>0,F54<F55),TRUE())),"OK","UZUPEŁNIJ / POPRAW"),"UZUPEŁNIJ / POPRAW")','','',True)
 section(62,'SCHEMAT ŚCIANY — AKTUALIZOWANY Z POWYŻSZYCH WYMIARÓW')
 for rr in range(64,81):s.row_dimensions[rr].height=22
 section(82,'05  SŁUPKI I DREWNO — WYBÓR KLASY ZAMIAST PRZEPISYWANIA E, G I ρ')
 for args in [(84,'Klasa / źródło danych','C24','','Klasa wybiera E, G i ρ z MATERIAŁY. Baza historyczna PN-EN 338:1999 wymaga potwierdzenia dla projektu.'),(85,'Szerokość przekroju b',45,'mm','Jednorodny przekrój wszystkich prętów w tym uproszczonym modelu.'),(86,'Wysokość przekroju h',145,'mm','Wymiar w lokalnej osi z pręta; orientację podaje dokumentacja modelu.')]:field(*args)
 for row,label,index,custom,unit,note in [(87,'E0,mean — moduł sprężystości',6,91,'MPa','Z PN-EN 338 / deklaracji drewna. E opisuje sztywność wzdłuż włókien; 1 MPa = 1 N/mm².'),(88,'Gmean — moduł ścinania',8,92,'MPa','Z tej samej klasy i źródła co E. G jest modułem materiału, nie obciążeniem stałym Gk.'),(89,'ρmean — gęstość średnia',11,93,'kg/m³','ρ (grecka litera rho), nie parcie p. Służy do obliczania ciężaru drewna.')]:
  field(row,label,f'=IFERROR(IF(F84="Dane własne",F{custom},VLOOKUP(F84,MATERIAŁY!$A$6:$K$8,{index},FALSE)),"")',unit,note,True)
 field(90,'Źródło właściwości','=IF(F84="Dane własne",F94,"PN-EN 338:1999, tab. 1 — wydanie historyczne; potwierdź dla projektu")','','Baza nie stanowi potwierdzenia aktualności normy ani klasy konkretnej partii drewna.',True)
 for args in [(91,'Dane własne: E',11000,'MPa','Używane wyłącznie po wyborze „Dane własne”.'),(92,'Dane własne: G',690,'MPa','Nie wyznaczaj arbitralnie jako E/16, gdy źródło podaje inną wartość.'),(93,'Dane własne: ρ',420,'kg/m³','Średnia gęstość dla ciężaru własnego; nie mylić z charakterystyczną gęstością ρk.'),(94,'Dane własne: źródło',None,'','Numer deklaracji / dokument / wydanie / tabela.')]:field(*args)
 listval('F84',['C18','C24','C30','Dane własne']);s.row_dimensions.group(91,94,outline_level=1,hidden=True)
 section(96,'06  REAKCJE Z PAMIRA / SIŁY DZIAŁAJĄCE NA ŚCIANĘ — OPCJONALNE')
 merge(97,2,15,'Rozwiń grupę wierszy. Jednostki kN i kNm; Y pionowo, Z poza ścianę. Wpisuj działania dachu NA ŚCIANĘ. Jeżeli Pamir podaje reakcję podpory na wiązar, odwróć znak. Węzły 1–3: wieniec; 4–6: góra.',YELLOW);s.row_dimensions[97].height=36
 for cc,title in enumerate(['Przypadek','Węzeł','Fx kN','Fy kN','Fz kN','Mx kNm','My kNm','Mz kNm'],2):s.cell(98,cc,title).fill=PatternFill('solid',fgColor=GRAY)
 wall=w['ŚCIANA – DANE']
 for case,name in enumerate(['G','S','W+','W−','Q','DOD']):
  for n in range(6):
   r=99+case*6+n;s.cell(r,2,name);s.cell(r,3,n+1)
   for axis in range(6):
    original=wall.cell(36+case*6+n,2+axis).value
    s.cell(r,4+axis,original if isinstance(original,(int,float)) else 0).fill=PatternFill('solid',fgColor=BLUE)
    wall.cell(36+case*6+n,2+axis,f"='DANE WEJŚCIOWE'!{C(4+axis)}{r}")
 s.row_dimensions.group(98,134,outline_level=1,hidden=True)
 section(136,'07  LIMITY UŻYTKOWNIKA — NIE ZASTĘPUJĄ PEŁNYCH SPRAWDZEŃ NORMOWYCH')
 field(138,'Limit u węzłów',None,'mm','Opcjonalny, z uzasadnionego kryterium projektowego; brak automatycznego limitu normowego.')
 field(139,'Limit naprężenia końcowego',None,'MPa','Wyłącznie kontrola przesiewowa. Nie obejmuje stateczności, połączeń i normowej interakcji.')
 merge(142,2,15,'Pełne sprawdzenia normowe, połączenia i stateczność pozostają NIEZWERYFIKOWANE. Strefa, wysokość n.p.m. i kategoria terenu są danymi do raportu, a nie ukończonym generatorem qp i sk.',YELLOW);s.row_dimensions[142].height=36
 s.cell(144,2,'→ ŚCIANA SZCZYTOWA — SCHEMAT I WYNIKI').hyperlink="#'ŚCIANA SZCZYTOWA'!B2"
 for rr in [10,11,13,18,19,30,31,32,33,34,40,41,42,43,50,51,52,53,54,85,86,91,92,93]:numval(f'F{rr}')
 s.sheet_properties.pageSetUpPr.fitToPage=True;s.page_setup.orientation='portrait';s.page_setup.paperSize=s.PAPERSIZE_A4;s.page_setup.fitToWidth=1;s.page_setup.fitToHeight=0;s.print_options.horizontalCentered=True;s.print_area='B1:O144'
 # Historical source data, with explicit provenance; do not infer current normative editions.
 mat=w['MATERIAŁY'];mat['K5']='ρmean kg/m³'
 for rr,vals in [(6,[9000,6000,560,320,380]),(7,[11000,7400,690,350,420]),(8,[12000,8000,750,380,460])]:
  for cc,value in zip([6,7,8,9,11],vals):mat.cell(rr,cc,value)
  mat.cell(rr,10,'PN-EN 338:1999, tab. 1 (historyczna)')
 mat['A12']='E0,mean, E0,05, Gmean, ρk i ρmean: PN-EN 338:1999 tab.1 z załączonego źródła. To starsze wydanie; nie potwierdzono aktualności zestawu dla projektu. Gęstość do ciężaru własnego pobierana jest z ρmean, nie ρk.'
 # Bridge archived inputs to the single visible form. Existing advanced data remain preserved.
 links={19:53,20:50,21:51,22:52,25:54,27:55,28:59,29:50,34:30,35:32,36:31,37:10,40:33,42:34,43:35,47:9,48:11,49:12,50:13,54:16,56:18,57:19,58:14,59:15,64:21,65:22,71:44,72:40,73:42,76:43,94:41}
 for rr,newrow in links.items():old.cell(rr,2,f"='DANE WEJŚCIOWE'!F{newrow}")
 old['B26']='=IF(\'DANE WEJŚCIOWE\'!F49="Prostokąt","Prostokątna",IF(\'DANE WEJŚCIOWE\'!F49="Szczytowa jednospadowa","Trapezowa","Trójkątna"))'
 old['B30']="='DANE WEJŚCIOWE'!F60";old['B144']="='DANE WEJŚCIOWE'!F55"
 old['B147']='=IF(AND(\'DANE WEJŚCIOWE\'!F60="OK",COUNT(\'DANE WEJŚCIOWE\'!F21:F22,\'DANE WEJŚCIOWE\'!F87:F89)=5,MIN(\'DANE WEJŚCIOWE\'!F21:F22)>=0,MIN(\'DANE WEJŚCIOWE\'!F87:F89)>0,\'DANE WEJŚCIOWE\'!F90<>""),"OK","BLOKADA — SPRAWDŹ DANE ŚCIANY")'
 # Single panel now contains only links/results, never a second set of inputs.
 main=w['ŚCIANA SZCZYTOWA']
 for addr,row in {'C6':50,'F6':53,'I6':52,'C8':54,'F8':51,'I8':49,'C10':55,'F10':59,'C27':85,'F27':86,'C29':87,'F29':88,'I29':89,'C33':21,'F33':22,'I33':43,'I35':44,'F39':138,'F41':139}.items():
  main[addr]=f"='DANE WEJŚCIOWE'!F{row}";main[addr].fill=PatternFill('solid',fgColor=GRAY)
 main['B31']='OBCIĄŻENIA PRZYJĘTE Z FORMULARZA — WARTOŚCI CHARAKTERYSTYCZNE [N/m²]'
 main['B25']='PRZEKRÓJ I PARAMETRY DREWNA — AUTOMATYCZNIE Z DANYCH WEJŚCIOWYCH'
 main['E4']="=IF('DANE WEJŚCIOWE'!F4=\"\",\"\",'DANE WEJŚCIOWE'!F4)";main['E4'].fill=PatternFill('solid',fgColor=GRAY)
 for addr,rr in [('F39',138),('F41',139)]:main[addr]=f"=IF(ISNUMBER('DANE WEJŚCIOWE'!F{rr}),'DANE WEJŚCIOWE'!F{rr},\"\")"
 main['B2']='Ściana szczytowa — schemat i wyniki (dane wpisuj w DANE WEJŚCIOWE)'
 main['B50']='Pełna kontrola normowa, stateczność, poszycie i połączenia: NIEZWERYFIKOWANE. Schemat odwzorowuje wybrany kształt; trzy słupki to uproszczona topologia modelu.'
 main['B53']='→ Jedyny formularz danych';main['B53'].hyperlink="#'DANE WEJŚCIOWE'!B1"
 main['E53']='Źródła E/G/ρ: MATERIAŁY';main['H53']='Źródła obciążeń: NORMY'
 main['E53'].hyperlink="#'MATERIAŁY'!A5";main['H53'].hyperlink="#'NORMY'!A5"
 main._charts=[]
 for cc in range(12,45):main.column_dimensions[C(cc)].hidden=True
 main.print_area='B1:J53'
 # Correct geometric model, including zero-height corner nodes via aliasing/inactive elements.
 for n,newrow in enumerate([56,57,58]):wall.cell(20+n,3,f"='DANE WEJŚCIOWE'!F{newrow}")
 wall['J75']='Aktywny pręt'
 for m in range(7):
  rr=76+m;wall.cell(rr,10,f'=IF(C{20+m}>0,1,0)' if m<3 else 1)
  for cc,newrow in [(4,85),(5,86),(6,87),(7,88),(8,89)]:wall.cell(rr,cc,f"='DANE WEJŚCIOWE'!F{newrow}")
 wall['B81']='=IF(C20=0,1,4)';wall['C82']='=IF(C22=0,3,6)'
 for n in [0,1,2]:
  for axis in range(6):wall.cell(29+n,2+axis,f'=IF(C{20+n}=0,1,0)')
 wall['A130']='Model XY: Y pionowo, Z poza ścianę. Nieaktywne słupki o wysokości 0 pominięto; oczep jest połączony z dolnym narożnikiem. Obciążenia dachu przekazuje się przez siły węzłowe. Rozdział wiatru jest modelem pasm, nie analizą poszycia.'
 # Triangular/trapezoidal area-conserving tributary width, never full wall load per stud.
 for case in range(6):
  for m in range(7):
   rr=86+case*7+m;mr=76+m
   for axis in range(3):
    f=wall.cell(rr,3+axis).value
    if case in [2,3] and m<3 and axis==2:
     f=f'=IFERROR({1 if case==2 else -1}*$B${9 if case==2 else 10}*($B$5*{[.25,.5,.25][m]})/1000,0)'
    if isinstance(f,str) and f.startswith('='):wall.cell(rr,3+axis,f'=IF($J${mr}=0,0,{f[1:]})')
 # Guard inactive element matrices only. The placeholder length has no stiffness or load.
 matrix=w['A – MACIERZE']
 for m in range(7):
  base=5+68*m;mr=76+m;flag=f"'ŚCIANA – DANE'!$J${mr}"
  f=matrix.cell(base,2).value;matrix.cell(base,2,f'=IF({flag}=0,1,{f[1:]})')
  for i in range(3):
   for j in range(3):
    c=matrix.cell(base+1+i,8+j);f=c.value;c.value=f'=IF({flag}=0,{int(i==j)},{f[1:]})'
  for rr in range(base+6,base+18):
   for cc in range(2,14):
    c=matrix.cell(rr,cc);f=c.value;c.value=f'=IF({flag}=0,0,{f[1:]})'
 # Schemes use their own coordinates, not the legacy chart's wrong shape or unsupported bounds.
 for target in [s,main]:
  for cc in range(27,45):target.column_dimensions[C(cc)].hidden=True
  # Physical scale kept equal in both directions on a 2:1 plot; axes are hidden, dimensions are printed in cells.
  pts=[('0','0'),('0',"'DANE WEJŚCIOWE'!F56"),("'DANE WEJŚCIOWE'!F50/2","'DANE WEJŚCIOWE'!F57"),("'DANE WEJŚCIOWE'!F50","'DANE WEJŚCIOWE'!F58"),("'DANE WEJŚCIOWE'!F50",'0'),('0','0')]
  den="MAX('DANE WEJŚCIOWE'!F50,2*'DANE WEJŚCIOWE'!F55)"
  for i,(x,y) in enumerate(pts,2):
   target.cell(i,27,f'=IFERROR((1-0.9*\'DANE WEJŚCIOWE\'!F50/({den}))/2+0.9*({x})/({den}),0)')
   target.cell(i,28,f'=IFERROR(0.05+1.8*({y})/({den}),0)')
  chart=ScatterChart();chart.scatterStyle='line';chart.width=20 if target==s else 15;chart.height=10 if target==s else 7.5;chart.legend=None;chart.visible_cells_only=False;chart.x_axis.majorGridlines=None;chart.y_axis.majorGridlines=None
  series=Series(Reference(target,min_col=28,min_row=2,max_row=7),Reference(target,min_col=27,min_row=2,max_row=7),title='Obrys ściany')
  series.smooth=False;series.graphicalProperties.line.solidFill=INK;series.graphicalProperties.line.width=28000;chart.series.append(series)
  for m in range(3):
   for k in range(2):
    rr=12+m*3+k
    target.cell(rr,27,f'=IFERROR((1-0.9*\'DANE WEJŚCIOWE\'!F50/({den}))/2+0.9*\'DANE WEJŚCIOWE\'!F50*{m}/2/({den}),0)')
    target.cell(rr,28,f'=IFERROR(0.05+1.8*\'DANE WEJŚCIOWE\'!F{56+m}*{k}/({den}),0)')
   ser=Series(Reference(target,min_col=28,min_row=12+m*3,max_row=13+m*3),Reference(target,min_col=27,min_row=12+m*3,max_row=13+m*3),title=f'Słupek {m+1}')
   ser.smooth=False;ser.graphicalProperties.line.solidFill='6383A0';chart.series.append(ser)
  chart.x_axis.scaling.min=0;chart.x_axis.scaling.max=1;chart.y_axis.scaling.min=0;chart.y_axis.scaling.max=1
  chart.x_axis.delete=True;chart.y_axis.delete=True
  target.add_chart(chart,'B64' if target==s else 'B11')
 # Only useful wall-facing tabs remain visible; all outrigger and legacy administration are retained but hidden.
 visible=['DANE WEJŚCIOWE','ŚCIANA SZCZYTOWA','ŚCIANA – WYNIKI','KOMBINACJE','MATERIAŁY','NORMY']
 for sh in w:sh.sheet_state='visible' if sh.title in visible else 'hidden'
 w._sheets=[w[n] for n in visible]+[sh for sh in w if sh.title not in visible]
 w.active=0;w.calculation=CalcProperties(calcId=0,fullCalcOnLoad=True,forceFullCalc=True)
 Path(output).parent.mkdir(parents=True,exist_ok=True);w.save(output)

if __name__=='__main__':rebuild(sys.argv[1],sys.argv[2])
