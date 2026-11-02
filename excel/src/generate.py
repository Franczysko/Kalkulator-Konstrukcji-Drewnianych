"""Generate a standalone Excel 365 workbook. No VBA, external links or Python at runtime."""
from pathlib import Path
from math import pi
import sys
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell as cell, xl_col_to_name as col

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output'/'Kalkulator_konstrukcji_drewnianych.xlsx'


def ref(sheet, addr):
    return f"'{sheet}'!{addr}"


class Builder:
    def __init__(self, output=OUT):
        self.w = xlsxwriter.Workbook(str(output))
        self.w.set_properties({'title': 'Konstrukcje drewniane — ściany i wysuwnice', 'author': 'Kalkulator Konstrukcji Drewnianych', 'comments': 'Model badawczy 3D; nie jest kompletną weryfikacją projektową.'})
        self.w.set_calc_mode('auto')
        self.f = {}
        common = {'font_name': 'Calibri', 'font_size': 10, 'valign': 'vcenter'}
        for key, extra in {
            'text': {}, 'title': {'font_size': 15, 'bold': True, 'bottom': 2},
            'section': {'bold': True, 'bg_color': '#E4E7EB', 'bottom': 1},
            'input': {'bg_color': '#CCDEF3', 'border': 1, 'num_format': '0.000', 'locked': False},
            'input_text': {'bg_color': '#CCDEF3', 'border': 1, 'locked': False},
            'auto': {'bg_color': '#F0F0F0', 'border': 1, 'num_format': '0.000'},
            'warn': {'bg_color': '#FFF2B3', 'text_wrap': True, 'border': 1},
            'note': {'font_size': 9, 'text_wrap': True, 'font_color': '#545B63'},
            'head': {'bold': True, 'bg_color': '#DEE6EE', 'border': 1, 'text_wrap': True},
            'number': {'num_format': '0.000000', 'font_size': 9},
            'percent': {'num_format': '0.0%', 'bg_color': '#FFF2B3', 'border': 1},
            'pass': {'bg_color': '#D5EEDC', 'font_color': '#166534'},
            'fail': {'bg_color': '#FADBD8', 'font_color': '#9F2222'},
        }.items(): self.f[key] = self.w.add_format(common | extra)
        self.s = {}
        for name in ['START', 'ŚCIANA – DANE', 'ŚCIANA – OBLICZENIA', 'ŚCIANA – WYNIKI',
                     'WYSUWNICA – DANE', 'WYSUWNICA – OBLICZENIA', 'WYSUWNICA – WYNIKI',
                     'KOMBINACJE', 'MATERIAŁY', 'NORMY', 'RAPORT', 'TESTY',
                     'MODEL A', 'OBCIĄŻENIA A', 'MES A', 'MODEL B', 'OBCIĄŻENIA B', 'MES B']:
            s = self.w.add_worksheet(name); self.s[name] = s
            s.hide_gridlines(2); s.set_default_row(19); s.set_column('A:P', 8.5)
            s.set_landscape(); s.set_paper(9); s.fit_to_pages(1, 0)
            s.set_margins(.3, .3, .4, .4); s.set_footer('&LProjekt badawczy — zakres ograniczony&C&P / &N&R2026-11-02')
            s.freeze_panes(5, 1); s.set_tab_color('#356A91')
        self.start(); self.norms(); self.materials(); self.combos()
        self.data('A'); self.data('B')
        for code in 'AB': self.model(code); self.loads(code); self.solver(code); self.calcs(code); self.results(code)
        self.report(); self.tests()
        self.w.close()

    def merge(self, s, row, first, last, text, style='text'):
        s.merge_range(row, first, row, last, text, self.f[style])

    def title(self, s, title, subtitle):
        self.merge(s, 1, 1, 14, title, 'title'); s.set_row(1, 30)
        self.merge(s, 3, 1, 14, subtitle, 'note'); s.set_row(3, 32)

    def formula(self, s, r, c, formula, style='number'):
        s.write_formula(r, c, formula if formula.startswith('=') else '='+formula, self.f[style])

    def start(self):
        s = self.s['START']; self.title(s, 'KALKULATOR KONSTRUKCJI DREWNIANYCH', 'Karty obliczeniowe w stylistyce Gable panel stud • Excel 365 • wersja 0.2 / 02.11.2026')
        items = [
            ('ZAKRES', 'Samodzielny solver liniowej ramy przestrzennej: 6 węzłów, 7 prętów, 36 stopni swobody. Ściana i wysuwnica są osobnymi modelami 3D.'),
            ('STATUS WYDANIA', 'NIEZWERYFIKOWANE DO PEŁNEGO PROJEKTOWANIA. Mechanika prętów działa; brak kompletnej weryfikacji normowej, przepon, połączeń i stateczności całego układu.'),
            ('OBSŁUGA', '1. Edytuj niebieskie pola w DANE. 2. Sprawdź MODEL i warunki podparcia. 3. Uzupełnij obciążenia i współczynniki. 4. Odczytaj WYNIKI i RAPORT.'),
            ('POLA', 'Niebieskie: dane użytkownika; szare: formuły; żółte: braki/ograniczenia; czerwone: przekroczenie kontroli częściowej; zielone: zaliczony test lub pojedyncza kontrola.'),
            ('NORMY', 'Udokumentowano dostarczone wydania historyczne. Dostęp do katalogu PKN otrzymał 403. Nie potwierdzono stanu wydań, zmian i NA na 2026 r.'),
            ('KOMBINACJE', '6 przypadków charakterystycznych działa od razu. Generator SGN/SGU wymaga wpisania współczynników PN-EN 1990 i potwierdzenia ich źródła w NORMY. Brak danych nie jest zastępowany domyślnymi wartościami normowymi.'),
            ('MODELE', 'Węzły sztywne; brak zwolnień końcowych, podatności połączeń, efektów II rzędu, paczenia, kontaktu i podpór jednostronnych. Pręty Eulera–Bernoulliego. Nie sumuje się dwóch analiz 2D.'),
            ('RYSUNKI', 'Wykresy XY są połączone z komórkami modelu i aktualizują się po zmianie danych. Schematy są rzutami, nie rysunkami wykonawczymi ani potwierdzeniem sztywności łączników.'),
            ('DANE POCZĄTKOWE', 'Geometria i obciążenia są przykładem technicznym, a nie projektem. Wartości drewna z PN-EN 338:1999 są historyczne i wymagają zastąpienia potwierdzonymi danymi dla przyjętego zestawu norm.'),
            ('NIEZALEŻNOŚĆ', 'Formuły działają bez Pythona, makr i zewnętrznego solvera. Python służy wyłącznie do generacji i testów. Nie opublikowano załączonych norm ani arkusza wzorcowego.'),
        ]
        for i,(label,txt) in enumerate(items):
            r=6+i*4; self.merge(s,r,1,14,label,'section'); self.merge(s,r+1,1,14,txt,'warn' if i in [1,4] else 'note'); s.set_row(r+1,44)
        self.merge(s,48,1,5,'Nazwa inwestycji'); s.merge_range('G49:O49','Projekt przykładowy',self.f['input_text'])
        self.merge(s,50,1,5,'Numer projektu'); s.merge_range('G51:O51','DEMO-001',self.f['input_text'])
        self.merge(s,52,1,5,'Data raportu'); s.merge_range('G53:O53','2026-11-02',self.f['input_text'])
        for r, name in [(55,'ŚCIANA – DANE'),(57,'WYSUWNICA – DANE'),(59,'NORMY'),(61,'RAPORT')]:
            s.write_url(r,1,f"internal:'{name}'!B2",self.f['section'],string='→ '+name)
        s.print_area(0,0,63,15)

    def norms(self):
        s=self.s['NORMY']; self.title(s,'PODSTAWA OBLICZEŃ I ŹRÓDŁA','Bez mieszania generacji Eurokodów. Aktualność PKN niepotwierdzona — 403 z sieci środowiska.')
        headers=['Dokument / metoda','Wydanie / lokalizacja','Użycie i ograniczenia']
        for c,h in zip([1,5,9],headers):self.merge(s,5,c,c+3,h,'head')
        rows=[
          ('PN-EN 1995-1-1','2010; EN 2004+AC:2006+A1:2008; NA w załączniku pliku','Odczytano skan. kmod tab.3.1, kdef tab.3.2, γM tab.2.3 / NA.2. Nie potwierdzono późniejszych zmian.'),
          ('PN-EN 338','1999; tablica 1, strona 7','C18/C24/C30 historyczne; nie traktować jako aktualnej bazy normowej.'),
          ('PN-EN 1991-1-1','2004; załącznik EUF424_1.PDF','Identyfikacja okładki OCR. Obciążenia użytkownik podaje bezpośrednio; brak automatycznego odczytu tabel.'),
          ('PN-EN 1991-1-3','2005; skan użytkownika','Brak automatycznej strefy śniegowej, μ, Ce, Ct i NA. S jest wejściowym obciążeniem na rzut poziomy.'),
          ('PN-EN 1991-1-4','Skan 152 strony; wydanie do potwierdzenia','W+ i W− to niezależne wartości netto na powierzchnię, po cpe/cpi; brak wyznaczania stref i szczytowego ciśnienia.'),
          ('PN-EN 1990 + NA','Nie dostarczono kompletnego źródła; PKN zablokowany','Pola γG, γQ, ψ0, ψ2 pozostawiono puste. Generator aktywny dopiero po uzupełnieniu.'),
          ('PN-EN 14250','Brak zweryfikowanego wydania','Płytki kolczaste i kontrola prefabrykacji niezaimplementowane.'),
          ('Dokumentacje producentów','Dostarczono ETA, deklaracje i poradniki','Nie uogólniono nośności. Dobór konkretnego produktu, podłoża i geometrii pozostaje wymagany.'),
          ('Statyka ram 3D','Metoda przemieszczeń, liniowa mechanika','Ku=F, R=Ku−F, k_global=Tᵀ k_local T. Zobacz docs/OBLICZENIA.md i jawne macierze MES A/B.'),
          ('Przekrój prostokątny','Mechanika: A=bh, Iy=bh³/12, Iz=hb³/12','N/mm², mm; σ=N/A, σmy=My/Wy, σmz=Mz/Wz. Brak redukcji przez karby, otwory i pożar.'),
          ('Skręcanie Saint-Venanta','Szereg Fouriera, 25 wyrazów nieparzystych','J=ab³/3·[1−192b/(π⁵a)·Σtanh(nπa/2b)/n⁵], a≥b. Brak paczenia i kontroli nośności skrętnej.'),
          ('Kontrole przekrojowe EC5','2.4.1(2.14), 6.1.6(6.11–12), 6.2.3–4(6.17–20)','Interakcja z rozciąganiem/ściskaniem i dwukierunkowym zginaniem; km=0.7 dla prostokąta. Bez wyboczenia i zwichrzenia: wyłącznie kontrola częściowa.'),
          ('Szerokości wpływu ściany','Model rozdziału p na 3 słupki: W/4,W/2,W/4','Suma sił odpowiada polu trapezu/szczytu; nie jest analizą sztywności poszycia ani dowodem rozdziału rzeczywistego.'),
          ('Model wysuwnicy','2 podłużnice × 3 stacje; pełne sprzężenie 3D','Poprzeczki mają pasma a/2,(a+c)/2,c/2. W jest długością po połaci; S działa na rzut poziomy.'),
        ]
        for i,(a,b,c) in enumerate(rows):
            r=7+i*3
            for first,last,text in [(1,4,a),(5,8,b),(9,14,c)]:self.merge(s,r,first,last,text,'note')
            s.set_row(r,49)
        self.merge(s,52,1,14,'WSPÓŁCZYNNIKI PN-EN 1990 — DANE PROJEKTANTA, BEZ DOMYŚLNYCH WARTOŚCI','section')
        labels=['γG niekorzystne','γG korzystne','γQ','ψ0 śnieg','ψ0 wiatr','ψ0 użytkowe / H / Q','ψ2 śnieg','ψ2 wiatr','ψ2 użytkowe / H / Q']
        for i,label in enumerate(labels):
            r=54+i; self.merge(s,r,1,5,label);s.write_blank(r,6,None,self.f['input'])
            s.data_validation(r,6,r,6,{'validate':'decimal','criteria':'between','minimum':0,'maximum':3})
        self.merge(s,64,1,5,'Źródło / wydanie / punkt');s.merge_range('G65:O65','',self.f['input_text'])
        self.merge(s,66,1,5,'Aktualny zestaw potwierdzony?');s.write('G67','NIE',self.f['input_text']);s.data_validation('G67',{'validate':'list','source':['NIE','TAK']})
        self.formula(s,68,6,'IF(AND(COUNT(G55:G63)=9,G65<>"",G67="TAK"),1,0)','auto')
        self.merge(s,69,1,14,'Potwierdzenie pól nie usuwa ograniczeń modelu i nie włącza ogólnego wyniku SPEŁNIA. Pełna analiza połączeń i stateczności pozostaje niewykonana.','warn');s.set_row(69,34)
        s.print_area(0,0,70,15)

    def materials(self):
        s=self.s['MATERIAŁY'];self.title(s,'BAZA MATERIAŁOWA','Historyczne dane PN-EN 338:1999, tab.1. Edytowalne; wydanie i przydatność wymagają potwierdzenia.')
        headers=['Klasa','fm,k','ft,0,k','fc,0,k','fv,k','E0,mean','E0,05','Gmean','ρmean','Źródło']
        for c,h in enumerate(headers,1):s.write(5,c,h,self.f['head'])
        data=[['C18',18,11,18,2.0,9000,6000,560,380],['C24',24,14,21,2.5,11000,7400,690,420],['C30',30,18,23,3.0,12000,8000,750,460]]
        for r,row in enumerate(data,6):
            for c,v in enumerate(row,1):s.write(r,c,v,self.f['input_text'] if c==1 else self.f['input'])
            s.write(r,10,'PN-EN 338:1999 / tab.1',self.f['note'])
        self.merge(s,10,1,14,'Wytrzymałość i moduły: N/mm²; gęstość: kg/m³. fv z wydania 1999 nie jest automatycznie wartością właściwą dla nowszej edycji.','warn');s.set_row(10,35)
        self.merge(s,13,1,14,'DREWNO LITE — PN-EN 1995-1-1:2010, TAB. 3.1 / 3.2','section')
        for c,v in enumerate(['Klasa użytkowania','Stałe','Długotrwałe','Średniotrwałe','Krótkotrwałe','Chwilowe','kdef'],1):s.write(15,c,v,self.f['head'])
        for r,row in enumerate([[1,.6,.7,.8,.9,1.1,.6],[2,.6,.7,.8,.9,1.1,.8],[3,.5,.55,.65,.7,.9,2.0]],16):
            for c,v in enumerate(row,1):s.write(r,c,v,self.f['input'])
        self.merge(s,20,1,14,'NA.1 w dostarczonym wydaniu: śnieg — średniotrwałe, wiatr — krótkotrwałe. H i Q przyjęto jako średniotrwałe, wymaga sprawdzenia dla danego oddziaływania.','note');s.set_row(20,35)
        self.merge(s,23,1,5,'γM drewno lite (tab.2.3)');s.write('G24',1.3,self.f['input'])
        self.merge(s,25,1,14,'OSB/3 i OSB/4: brak bazy sztywności, nośności i łączników dla wybranego produktu. Poszycie nie jest traktowane jako stężenie.','warn');s.set_row(25,35)
        for r,v in enumerate(['45×95','45×145','45×170','45×195','Własny'],30):s.write(r,1,v,self.f['input_text'])
        self.w.define_name('TimberClasses',"='MATERIAŁY'!$B$7:$B$9")
        self.w.define_name('Sections',"='MATERIAŁY'!$B$31:$B$35")
        s.print_area(0,0,36,15)

    def combos(self):
        s=self.s['KOMBINACJE'];self.title(s,'PRZYPADKI I KOMBINACJE','G/S/W+/W−/H/Q; wiatr parcie i ssanie wzajemnie wykluczające. ULS/SLS zależne od danych NORMY.')
        heads=['ID','Rodzaj','Opis','G','S','W+','W−','H','Q','Aktywna','kmod A','kmod B']
        for c,h in enumerate(heads,1):s.write(5,c,h,self.f['head'])
        self.combo_rows=[]
        for i in range(6):
            r=6+i;self.combo_rows.append(r)
            s.write(r,1,f'K{i+1:02}');s.write(r,2,'CHAR');s.write(r,3,['G','S','W+','W−','H','Q'][i])
            for j in range(6):s.write(r,4+j,int(i==j),self.f['auto'])
            s.write(r,10,1,self.f['auto'])
        n=6
        for favorable in [False,True]:
            specs=[(lead,wind) for lead in range(1,6) for wind in ([lead] if lead in [2,3] else [2,3])]+[(0,0)]
            for lead,wind in specs:
                r=6+n;self.combo_rows.append(r);n+=1
                s.write(r,1,f'U{n-6:02}');s.write(r,2,'SGN');s.write(r,3,f'6.10 / {"G−" if favorable else "G+"} / '+['G','S','W+','W−','H','Q'][lead]+f' / W{wind}')
                self.formula(s,r,4,ref('NORMY','G56' if favorable else 'G55'),'auto')
                for j in range(1,6):
                    if lead==0 or (j in [2,3] and j!=wind):f='0'
                    else:f=ref('NORMY','G57')+('' if j==lead else '*'+ref('NORMY',{1:'G58',2:'G59',3:'G59',4:'G60',5:'G60'}[j]))
                    self.formula(s,r,4+j,f,'auto')
                self.formula(s,r,10,ref('NORMY','G69'),'auto')
        for i,kind in enumerate(['SGU char','SGU final']):
            r=6+n+i;self.combo_rows.append(r);s.write(r,1,f'S{i+1:02}');s.write(r,2,kind);s.write(r,3,'G + S prowadzące + wiatr parcie towarzyszący')
            for j,f in enumerate(['1','1',ref('NORMY','G59'),'0','0','0']):self.formula(s,r,4+j,f,'auto')
            self.formula(s,r,10,ref('NORMY','G69'),'auto')
        for r in self.combo_rows:
            for code,c in [('A',11),('B',12)]:
                data='ŚCIANA – DANE' if code=='A' else 'WYSUWNICA – DANE'
                sc=ref(data,'$F$32')
                # Choose shortest duration present among nonzero actions; independent for each combination.
                duration=f'IF(OR(G{r+1}<>0,H{r+1}<>0),5,IF(OR(F{r+1}<>0,I{r+1}<>0,J{r+1}<>0),4,2))'
                self.formula(s,r,c,f'INDEX(\'MATERIAŁY\'!$C$17:$G$19,{sc},{duration}-1)','auto')
        self.merge(s,35,1,14,'SGN: wyłącznie kandydat 6.10, bez 6.10a/b, EQU, STR/GEO szczególnych sytuacji, wyjątkowych i sejsmicznych. Nie jest pełnym generatorem PN-EN 1990.','warn');s.set_row(35,38)
        self.merge(s,38,1,14,'SGU pokazuje przykład dla śniegu prowadzącego i parcia towarzyszącego. Brak kompletnej obwiedni SGU. CHAR to przypadki jednostkowe, nie kombinacje projektowe.','warn');s.set_row(38,38)
        s.set_column('D:D',27);s.print_area(0,0,41,14)

    def field(self,s,r,label,value,unit='',right=False,source=''):
        a,b,c=(8,12,14) if right else (1,5,7)
        self.merge(s,r,a,b-1,label)
        if isinstance(value,str) and value.startswith('='):s.merge_range(r,b,r,b+1,value,self.f['auto'])
        else:s.merge_range(r,b,r,b+1,value,self.f['input_text'] if isinstance(value,str) else self.f['input'])
        s.write(r,c,unit,self.f['note'])
        if source:s.write_comment(r,b,source)

    def data(self,code):
        wall=code=='A';name='ŚCIANA – DANE' if wall else 'WYSUWNICA – DANE';s=self.s[name]
        self.title(s,'ŚCIANA SZKIELETOWA — KARTA DANYCH' if wall else 'WYSUWNICA PREFABRYKOWANA — KARTA DANYCH','Niebieskie pola = dane. Szare = formuły. Schemat ramy 3D; geometria i podpory wymagają zgodności z rzeczywistością.')
        self.merge(s,18,1,14,'GEOMETRIA I PRZEKROJE','section')
        if wall:
            fields=[(20,'Kształt','Prostokąt',''),(22,'Szerokość ściany',1200,'mm'),(24,'Wysokość lewa',2400,'mm'),(26,'Wysokość środkowa',3000,'mm'),(28,'Wysokość prawa',2400,'mm')]
            right=[(20,'Liczba słupków',3,'szt.'),(22,'Rozstaw osiowy','=F23/2','mm'),(24,'Przekrój słupków','45×145',''),(26,'Szerokość własna b',45,'mm'),(28,'Wysokość własna h',145,'mm')]
            s.data_validation('F21',{'validate':'list','source':['Prostokąt','Trapez','Szczyt','Własna']})
        else:
            fields=[(20,'Schemat','Ściana i wiązar',''),(22,'Wysięg poza ścianę',600,'mm'),(24,'Część wewnętrzna',1200,'mm'),(26,'Szerokość po połaci',1200,'mm'),(28,'Nachylenie połaci',30,'°')]
            right=[(20,'Podłużnice / poprzeczki','2 / 3','szt.'),(22,'Długość całkowita','=F23+F25','mm'),(24,'Przekrój podłużnic','45×145',''),(26,'Szerokość własna b',45,'mm'),(28,'Wysokość własna h',145,'mm')]
            s.data_validation('F21',{'validate':'list','source':['Ściana i wiązar','Wspornik','Własne podpory']})
        for r,l,v,u in fields:self.field(s,r,l,v,u)
        for r,l,v,u in right:self.field(s,r,l,v,u,True)
        s.data_validation('M25',{'validate':'list','source':'=Sections'})
        self.field(s,30,'Klasa drewna','C24');s.data_validation('F31',{'validate':'list','source':'=TimberClasses'})
        self.field(s,31,'Klasa użytkowania',2);s.data_validation('F32',{'validate':'integer','criteria':'between','minimum':1,'maximum':3})
        self.field(s,30,'b efektywne','=IF(M25="Własny",M27,VALUE(LEFT(M25,2)))','mm',True)
        self.field(s,31,'h efektywne','=IF(M25="Własny",M29,VALUE(MID(M25,4,3)))','mm',True)
        self.merge(s,33,1,14,'OBCIĄŻENIA CHARAKTERYSTYCZNE NETTO — ZNAKI GLOBALNE','section')
        self.field(s,35,'G pokrycie / pionowe',.5,'kN/m²')
        self.field(s,37,'S śnieg (rzut poziomy)',.8,'kN/m²')
        self.field(s,39,'W+ parcie (wartość ≥0)',.6,'kN/m²')
        self.field(s,41,'W− ssanie (wartość ≥0)',.9,'kN/m²')
        self.field(s,35,'H w płaszczyźnie',.2,'kN/m²',True)
        self.field(s,37,'Q dodatkowe pionowe',0,'kN/m²',True)
        self.field(s,39,'Limit przemieszczenia',10,'mm',True,source='Wartość przykładowa użytkownika, nie limit normowy. Wymaga uzasadnienia w raporcie projektu.')
        self.field(s,41,'Poszycie / przepona','Nie uwzględniać','',True)
        self.merge(s,44,1,14,'ZAŁOŻENIA MODELU I PODPARCIA','section')
        txt=('3 słupki, oczep i podwalina. Prostokąt: wysokość F25. Trapez: interpolacja skrajnych wysokości. Szczyt: środek F27. Dla wysokości skrajnej 0 pręt brzegowy jest wyłączony; narożnik połączony z dolnym węzłem.' if wall else '2 podłużnice, 3 poprzeczki. Podpory translacyjne na ścianie i przy wiązarze. Wspornik: utwierdzenie obu wewnętrznych węzłów. Własne podpory: edytuj sześć blokad każdego węzła w MODEL B.')
        self.merge(s,46,1,14,txt,'note');s.set_row(46,46)
        self.merge(s,49,1,14,'Wszystkie węzły wewnętrzne są SZTYWNE. Solver nie potwierdza sztywności płytek, kątowników ani wkrętów. Poszycie, otwory i stężenia nie są modelowane.','warn');s.set_row(49,34)
        self.merge(s,52,1,14,'Siły węzłowe i dodatkowe obciążenia liniowe: OBCIĄŻENIA '+code+'. Indywidualne przekroje i blokady DOF: MODEL '+code+'.','note');s.set_row(52,30)
        self.merge(s,55,1,5,'WYNIK OGÓLNY');self.merge(s,55,6,14,'='+ref('ŚCIANA – WYNIKI' if wall else 'WYSUWNICA – WYNIKI','G6'),'warn')
        self.merge(s,58,1,14,'Brak końcowego SPEŁNIA: nie wykonano pełnej kontroli połączeń, przepon, wyboczenia i zwichrzenia. Szczegóły i wyniki mechaniczne w WYNIKI.','warn');s.set_row(58,35)
        for addr in ['F23','F25','F27','F29','M27','M29']:
            s.data_validation(addr,{'validate':'decimal','criteria':'between','minimum':0,'maximum':100000})
        s.set_portrait();s.fit_to_pages(1,1);s.print_area(0,0,61,15)
        # Chart data follows MODEL formulas and is live, including changed coordinates.
        ch=self.w.add_chart({'type':'scatter','subtype':'straight_with_markers'})
        for ei in range(7):
            rr=50+ei*3
            ch.add_series({'categories':f"='MODEL {code}'!$B${rr+1}:$B${rr+2}",'values':f"='MODEL {code}'!$C${rr+1}:$C${rr+2}",'line':{'color':'#454545','width':2},'marker':{'type':'circle','size':3},'name':f'E{ei+1}'})
        ch.add_series({'categories':f"='MODEL {code}'!$B$76:$B$81",'values':f"='MODEL {code}'!$C$76:$C$81",'line':{'none':True},'marker':{'type':'triangle','size':7,'border':{'color':'#356A91'},'fill':{'color':'#356A91'}},'name':'Podpory translacyjne'})
        ch.set_title({'name':'Rzut X–Z ściany' if wall else 'Rzut X–Y wysuwnicy'})
        ch.set_legend({'none':True});ch.set_x_axis({'name':'X [mm]','major_gridlines':{'visible':False}});ch.set_y_axis({'name':'Z [mm]' if wall else 'Y [mm]','major_gridlines':{'visible':False}})
        ch.set_chartarea({'border':{'none':True}});ch.set_size({'width':430,'height':245});s.insert_chart('B6',ch,{'x_scale':.82,'y_scale':.88})
        self.merge(s,6,9,14,'OSIE I PODPORY','section')
        for r,text in [(8,'Ściana: płaszczyzna X–Z; parcie +Y.'),(10,'Wysuwnica: X — wysięg; Y/Z — połać.'),(12,'Czarne linie: pręty. Węzły: punkty.'),(14,'Węzły podpór i DOF: MODEL A/B.'),(16,'Obciążenia: wartości netto, nie qp.')]:self.merge(s,r,9,14,text,'note');s.set_row(r,23)

    def model(self,code):
        wall=code=='A';s=self.s['MODEL '+code];d='ŚCIANA – DANE' if wall else 'WYSUWNICA – DANE'
        self.title(s,'MODEL '+code+' — WĘZŁY I PRĘTY','X/Y/Z mm. Blokada 1 = przemieszczenie/obrót zerowy; 0 = swobodny. Można nadpisać niebieskie formuły podpór.')
        heads=['Węzeł','X','Y','Z','ux','uy','uz','rx','ry','rz']
        for c,h in enumerate(heads,1):s.write(5,c,h,self.f['head'])
        D=lambda a:ref(d,a)
        for n in range(6):
            r=6+n;s.write(r,1,n+1)
            if wall:
                x=f'{D("F23")}*{n%3}/2';y='0'
                if n<3:z='0'
                elif n==3:z=D('F25')
                elif n==4:z=f'IF({D("F21")}="Prostokąt",{D("F25")},IF({D("F21")}="Trapez",({D("F25")}+{D("F29")})/2,{D("F27")}))'
                else:z=f'IF({D("F21")}="Prostokąt",{D("F25")},{D("F29")})'
            else:
                x=[f'-{D("F25")}', '0', D('F23')][n%3]
                y=f'{D("F27")}*COS(RADIANS({D("F29")}))*{n//3}'
                z=f'{D("F27")}*SIN(RADIANS({D("F29")}))*{n//3}'
            for c,f in enumerate([x,y,z],2):self.formula(s,r,c,f,'auto')
            for k in range(6):
                if wall:
                    f='1' if n<3 else (f'IF(E{r+1}=0,1,0)' if n in [3,5] else '0')
                else:
                    f=f'IF({D("F21")}="Wspornik",{int(n in [0,3])},{int(n in [0,1,3,4] and k<3)})'
                self.formula(s,r,5+k,f,'input')
                s.data_validation(r,5+k,r,5+k,{'validate':'integer','criteria':'between','minimum':0,'maximum':1})
        self.merge(s,5,12,14,'Geometria i materiał kompletne','head')
        dims = f'AND({D("F23")}>0,{D("M31")}>0,{D("M32")}>0,{D("F25")}>0)' if not wall else f'AND({D("F23")}>0,{D("M31")}>0,{D("M32")}>0,{D("F25")}>=0,{D("F29")}>=0,MAX($E$10:$E$12)>0)'
        self.formula(s,6,12,f'IFERROR(IF(AND({dims},COUNT($H$17:$J$23)=21,MIN($H$17:$J$23)>0,{D("F32")}>=1,{D("F32")}<=3,\'MATERIAŁY\'!$G$24>0,VLOOKUP({D("F31")},\'MATERIAŁY\'!$B$7:$J$9,2,FALSE)>0,VLOOKUP({D("F31")},\'MATERIAŁY\'!$B$7:$J$9,3,FALSE)>0,VLOOKUP({D("F31")},\'MATERIAŁY\'!$B$7:$J$9,4,FALSE)>0),1,0),0)','auto')
        for c,h in enumerate(['Pręt','i','j','aktywny','b mm','h mm','E N/mm²','G N/mm²','ρ kg/m³'],1):s.write(15,c,h,self.f['head'])
        if wall:
            pairs=[(1,4),(2,5),(3,6),(1,2),(2,3),(4,5),(5,6)]
        else:pairs=[(1,2),(2,3),(4,5),(5,6),(1,4),(2,5),(3,6)]
        for m,(i,j) in enumerate(pairs):
            r=16+m;s.write(r,1,m+1)
            for c,n in [(2,i),(3,j)]:
                if wall and m in [5,6] and n in [4,6]:self.formula(s,r,c,f'IF(E{6+n}=0,{n-3},{n})','auto')
                else:s.write(r,c,n,self.f['auto'])
            self.formula(s,r,4,f'IF(E{10 if m==0 else 12}>0,1,0)' if wall and m in [0,2] else '1','auto')
            self.formula(s,r,5,D('M31'),'input');self.formula(s,r,6,D('M32'),'input')
            for c,idx in [(7,6),(8,8),(9,9)]:self.formula(s,r,c,f'IFERROR(VLOOKUP({D("F31")},\'MATERIAŁY\'!$B$7:$J$9,{idx},FALSE),0)','auto')
        self.merge(s,26,1,14,'Podpory: blokady translacji i obrotów należy uzasadnić rzeczywistymi połączeniami, a nie samą obecnością łącznika.','note')
        self.merge(s,28,1,14,'ŚCIANA: węzły 1/2/3 = podwalina, 4/5/6 = oczep. WYSUWNICA: 1/4 = wiązar, 2/5 = ściana, 3/6 = krawędź okapu. Utwierdzenia ściany są założeniem do odrębnego uzasadnienia.','warn');s.set_row(28,38)
        # chart series projection includes conditional node aliases, no disconnected line.
        for m in range(7):
            r=50+m*3;mr=17+m
            for k,endpoint in enumerate(['C','D']):
                self.formula(s,r+k,1,f'INDEX($C$7:$C$12,{endpoint}{mr})')
                self.formula(s,r+k,2,f'INDEX(${"E" if wall else "D"}$7:${"E" if wall else "D"}$12,{endpoint}{mr})')
        for n in range(6):
            rr=7+n
            for cc,axis in [(1,'C'),(2,'E' if wall else 'D')]:
                self.formula(s,75+n,cc,f'IF(SUM(F{rr}:H{rr})>0,{axis}{rr},"")')
        s.print_area(0,0,31,14)

    def loads(self,code):
        wall=code=='A';s=self.s['OBCIĄŻENIA '+code];d='ŚCIANA – DANE' if wall else 'WYSUWNICA – DANE';mo='MODEL '+code
        self.title(s,'OBCIĄŻENIA '+code+' — PRZYPADKI CHARAKTERYSTYCZNE','Liniowe w globalnych osiach: kN/m = N/mm. Siły węzłowe: kN; momenty: kNm. Niebieskie formuły można nadpisać.')
        s.write(5,1,'Pręt',self.f['head'])
        for case,name in enumerate(['G','S','W+','W−','H','Q']):
            for axis in range(3):s.write(5,2+case*3+axis,name+' '+['X','Y','Z'][axis],self.f['head'])
        D=lambda a:ref(d,a)
        for m in range(7):
            r=6+m;s.write(r,1,m+1)
            # self-weight on every active member, explicitly in global Z.
            sw=f'{ref(mo,f"J{17+m}")}*{ref(mo,f"F{17+m}")}*{ref(mo,f"G{17+m}")}*9.80665/1000000000*{ref(mo,f"E{17+m}")}'
            for case in range(6):
                vals=['0','0','0']
                if case==0:vals[2]='-'+sw
                if wall:
                    if m<3:
                        width=f'{D("F23")}*{[.25,.5,.25][m]}/1000'
                        if case in [0,1,5]:vals[2]+=f'-{D({0:"F36",1:"F38",5:"M38"}[case])}*{width}'
                        if case in [2,3]:vals[1]=f'{"" if case==2 else "-"}{D("F40" if case==2 else "F42")}*{width}'
                        if case==4:vals[0]=f'{D("M36")}*{width}'
                elif m>=4:
                    width=[f'{D("F25")}/2',f'({D("F25")}+{D("F23")})/2',f'{D("F23")}/2'][m-4]+'/1000'
                    ang=f'RADIANS({D("F29")})'
                    if case in [0,1,5]:vals[2]+=f'-{D({0:"F36",1:"F38",5:"M38"}[case])}*({width})'+(f'*COS({ang})' if case==1 else '')
                    if case in [2,3]:
                        mag=f'{D("F40" if case==2 else "F42")}*({width})';sign=1 if case==2 else -1
                        vals[1]=f'{sign}*({mag})*SIN({ang})';vals[2]=f'{-sign}*({mag})*COS({ang})'
                    if case==4:vals[0]=f'{D("M36")}*({width})'
                for axis,f in enumerate(vals):self.formula(s,r,2+case*3+axis,f,'input')
        self.merge(s,15,1,14,'SIŁY SKUPIONE W WĘZŁACH (DODAWANE DO OBCIĄŻEŃ LINIOWYCH)','section')
        for c,h in enumerate(['Przypadek','Węzeł','Fx kN','Fy kN','Fz kN','Mx kNm','My kNm','Mz kNm'],1):s.write(17,c,h,self.f['head'])
        for case,name in enumerate(['G','S','W+','W−','H','Q']):
            for n in range(6):
                r=18+case*6+n;s.write(r,1,name);s.write(r,2,n+1)
                for c in range(3,9):s.write(r,c,0,self.f['input'])
        self.merge(s,56,1,14,'Nieaktywne skrajne węzły ściany trójkątnej: siły węzłowe podawaj w aktywnym narożniku 1 lub 3. Obciążenie nieaktywnego węzła nie przechodzi na konstrukcję.','warn');s.set_row(56,35)
        s.set_column('C:T',11);s.set_landscape();s.print_area(0,0,58,19)

    def solver(self,code):
        s=self.s['MES '+code];mo='MODEL '+code;ld='OBCIĄŻENIA '+code
        self.title(s,'MES '+code+' — JAWNY SOLVER RAMY 3D','Macierze w N i mm. 6 węzłów × 6 DOF. Normalizacja diagonalna przed MINVERSE; brak ukrytych skryptów.')
        blocks=[]
        for m in range(7):
            r=10+m*75;blocks.append(r);mr=17+m
            self.merge(s,r,1,14,f'E{m+1}: DOF, długość, przekrój i osie lokalne','section')
            for a in range(12):
                ncol='C' if a<6 else 'D'
                self.formula(s,r+1,1+a,f'({ref(mo,ncol+str(mr))}-1)*6+{a%6+1}')
            coords=[]
            for axis in range(3):
                cc=col(2+axis)
                f=f'INDEX({ref(mo,f"${cc}$7:${cc}$12")},{ref(mo,"D"+str(mr))})-INDEX({ref(mo,f"${cc}$7:${cc}$12")},{ref(mo,"C"+str(mr))})'
                self.formula(s,r+2,1+axis,f)
                coords.append(cell(r+2,1+axis))
            self.formula(s,r+3,1,f'IF({ref(mo,"E"+str(mr))}=0,1,MAX(1,SQRT(SUMSQ(B{r+3}:D{r+3}))))')
            L=cell(r+3,1);A=cell(r+3,2);Iy=cell(r+3,3);Iz=cell(r+3,4);J=cell(r+3,5)
            b=ref(mo,'F'+str(mr));h=ref(mo,'G'+str(mr));E=ref(mo,'H'+str(mr));G=ref(mo,'I'+str(mr));active=ref(mo,'E'+str(mr))
            self.formula(s,r+3,2,f'MAX(1,{b}*{h})');self.formula(s,r+3,3,f'MAX(1,{b}*{h}^3/12)');self.formula(s,r+3,4,f'MAX(1,{h}*{b}^3/12)')
            aa=f'MAX(1,{b},{h})';bb=f'MAX(1,MIN({b},{h}))'
            series='+'.join(f'TANH({n}*PI()*{aa}/(2*{bb}))/{n}^5' for n in range(1,50,2))
            self.formula(s,r+3,5,f'{aa}*{bb}^3/3*(1-192*{bb}/(PI()^5*{aa})*({series}))')
            # R rows 3x3: e_x, e_y, e_z.
            for a in range(3):self.formula(s,r+5,1+a,f'{coords[a]}/{L}')
            self.formula(s,r+6,1,f'IF(SQRT(B{r+6}^2+C{r+6}^2)<1E-10,1,-C{r+6}/SQRT(B{r+6}^2+C{r+6}^2))')
            self.formula(s,r+6,2,f'IF(SQRT(B{r+6}^2+C{r+6}^2)<1E-10,0,B{r+6}/SQRT(B{r+6}^2+C{r+6}^2))')
            s.write(r+6,3,0)
            for a,f in enumerate([f'C{r+6}*D{r+7}-D{r+6}*C{r+7}',f'D{r+6}*B{r+7}-B{r+6}*D{r+7}',f'B{r+6}*C{r+7}-C{r+6}*B{r+7}']):self.formula(s,r+7,1+a,f)
            # k local at B:r+10 and T at P:r+10; global at AD:r+10.
            kexpr={}
            for ids,f in [([0,6],f'{E}*{A}/{L}'),([3,9],f'{G}*{J}/{L}')]:
                for i in range(2):
                    for j in range(2):kexpr[ids[i],ids[j]]=f'({f})*{1 if i==j else -1}'
            for ids,I,sgn in [([1,5,7,11],Iz,1),([2,4,8,10],Iy,-1)]:
                mat=[[('12',1),(f'6*{L}',sgn),('12',-1),(f'6*{L}',sgn)],[(f'6*{L}',sgn),(f'4*{L}^2',1),(f'6*{L}',-sgn),(f'2*{L}^2',1)],[('12',-1),(f'6*{L}',-sgn),('12',1),(f'6*{L}',-sgn)],[(f'6*{L}',sgn),(f'2*{L}^2',1),(f'6*{L}',-sgn),(f'4*{L}^2',1)]]
                for i in range(4):
                    for j in range(4):v,sign=mat[i][j];kexpr[ids[i],ids[j]]=f'{sign}*{E}*{I}/{L}^3*({v})'
            for i in range(12):
                for j in range(12):
                    self.formula(s,r+10+i,1+j,f'{active}*({kexpr.get((i,j),"0")})')
                    self.formula(s,r+10+i,15+j,cell(r+5+i%3,1+j%3) if i//3==j//3 else '0')
            kr=f'B{r+11}:M{r+22}';tr=f'P{r+11}:AA{r+22}';kg=f'AD{r+11}:AO{r+22}'
            s.write_array_formula(r+10,29,r+21,40,f'=MMULT(TRANSPOSE({tr}),MMULT({kr},{tr}))',self.f['number'])
            for case in range(6):
                # q_local in B:D rows r+25+case.
                for a in range(3):
                    rowrng=f'{col(1)}{r+6+a}:{col(3)}{r+6+a}'
                    lr=7+m;loadrange=ref(ld,f'{col(2+case*3)}{lr}:{col(4+case*3)}{lr}')
                    self.formula(s,r+25+case,1+a,f'{active}*SUMPRODUCT({rowrng},{loadrange})')
                qx,qy,qz=[cell(r+25+case,1+a) for a in range(3)]
                fs=[f'{qx}*{L}/2',f'{qy}*{L}/2',f'{qz}*{L}/2','0',f'-{qz}*{L}^2/12',f'{qy}*{L}^2/12',f'{qx}*{L}/2',f'{qy}*{L}/2',f'{qz}*{L}/2','0',f'{qz}*{L}^2/12',f'-{qy}*{L}^2/12']
                for a,f in enumerate(fs):self.formula(s,r+34+a,1+case,f)
            fl=f'B{r+35}:G{r+46}'
            s.write_array_formula(r+34,15,r+45,20,f'=MMULT(TRANSPOSE({tr}),{fl})',self.f['number'])
            # Extract global element displacements; local end forces are recovered after assembly.
            for a in range(12):
                for case in range(6):self.formula(s,r+49+a,1+case,f'INDEX($B$1151:$G$1186,{cell(r+1,1+a)},{case+1})')
            s.write_array_formula(r+49,15,r+60,20,f'=MMULT({tr},B{r+50}:G{r+61})',self.f['number'])
            for a in range(12):
                for case in range(6):self.formula(s,r+63+a,1+case,f'SUMPRODUCT({cell(r+10+a,1)}:{cell(r+10+a,12)},{col(15+case)}{r+50}:{col(15+case)}{r+61})-{cell(r+34+a,1+case)}')
            # SUMPRODUCT above horizontal vs vertical is not valid; use MMULT with INDEX scalar.
            for a in range(12):
                for case in range(6):
                    self.formula(s,r+63+a,1+case,f'INDEX(MMULT({kr},P{r+50}:U{r+61}),{a+1},{case+1})-{cell(r+34+a,1+case)}')
        self.blocks=blocks
        # K raw rows 601..636, columns B:AK.
        for i in range(36):
            s.write(599,1+i,i+1)
            for j in range(36):
                terms=[]
                for r in blocks:
                    dof=f'$B${r+2}:$M${r+2}';kg=f'$AD${r+11}:$AO${r+22}'
                    terms.append(f'IFERROR(INDEX({kg},MATCH({i+1},{dof},0),MATCH({j+1},{dof},0)),0)')
                self.formula(s,600+i,1+j,'+'.join(terms))
            node=i//6;axis=i%6
            self.formula(s,600+i,39,ref(mo,cell(6+node,5+axis)))
            self.formula(s,600+i,40,f'IF(AN{601+i}=1,1,SQRT(MAX(1,ABS({cell(600+i,1+i)}))))')
        # scaled, constrained K at rows 651..
        for i in range(36):
            for j in range(36):
                self.formula(s,650+i,1+j,f'IF(OR($AN{601+i}=1,$AN{601+j}=1),{int(i==j)},{cell(600+i,1+j)}/($AO{601+i}*$AO{601+j}))')
        s.write_array_formula(700,1,735,36,'=IFERROR(MINVERSE(B651:AK686),0)',self.f['number'])
        s.write_array_formula(750,1,785,36,'=MMULT(B651:AK686,B701:AK736)',self.f['number'])
        inverse_errors = [f'ABS({cell(750+i,1+j)}-{int(i==j)})' for i in range(36) for j in range(36)]
        # Excel has a 255-argument limit: use a helper maximum for each row.
        for i in range(36): self.formula(s,750+i,39,'MAX('+','.join(inverse_errors[i*36:(i+1)*36])+')')
        self.formula(s,1244,1,'IF(MAX(AN751:AN786)<1E-7,1,0)','auto')
        # F global + nodal
        for i in range(36):
            for case in range(6):
                terms=[]
                for r in blocks:terms.append(f'SUMIF($B${r+2}:$M${r+2},{i+1},{col(15+case)}{r+35}:{col(15+case)}{r+46})')
                # SUMIF criteria horizontal, sums vertical mismatch -> extract each matching DOF explicitly.
                terms=[]
                for r in blocks:
                    terms.append(f'IFERROR(INDEX(${col(15+case)}${r+35}:${col(15+case)}${r+46},MATCH({i+1},$B${r+2}:$M${r+2},0)),0)')
                n=i//6;axis=i%6
                nodal=ref(ld,cell(18+case*6+n,3+axis))
                self.formula(s,800+i,1+case,'+'.join(terms)+f'+{nodal}*{1000 if axis<3 else 1000000}')
                self.formula(s,900+i,1+case,f'IF($AN{601+i}=1,0,{cell(800+i,1+case)}/$AO{601+i})')
        s.write_array_formula(1000,1,1035,6,'=MMULT(B701:AK736,B901:G936)',self.f['number'])
        for i in range(36):
            for case in range(6):
                self.formula(s,1150+i,1+case,f'{cell(1000+i,1+case)}/$AO{601+i}')
                self.formula(s,1200+i,1+case,f'INDEX(MMULT($B$601:$AK$636,$B$1151:$G$1186),{i+1},{case+1})-{cell(800+i,1+case)}')
        self.merge(s,1240,1,14,'U: B1151:G1186 (mm, rad); R: B1201:G1236 (N, Nmm). Niezerowe R na swobodnym DOF wskazuje błąd numeryczny lub mechanizm.','note')
        s.set_column('B:AO',11);s.set_tab_color('#777777');s.print_area(0,0,8,15)

    def calcs(self,code):
        wall=code=='A';name='ŚCIANA – OBLICZENIA' if wall else 'WYSUWNICA – OBLICZENIA';s=self.s[name]
        d='ŚCIANA – DANE' if wall else 'WYSUWNICA – DANE';mo='MODEL '+code;me='MES '+code
        self.title(s,'ŚCIANA — OBLICZENIA' if wall else 'WYSUWNICA — OBLICZENIA','Siły i naprężenia: obwiednia po długości pręta. η przekroju nie zawiera stateczności, połączeń, ścinania ani skręcania.')
        heads=['Komb.','Pręt','Aktywna','kmod','N rozc. N','N ścisk. N','My max Nmm','Mz max Nmm','V max N','T max Nmm','fm,d','ft,d','fc,d','σt','σc','σmy','σmz','η przekrój','u max [mm]','Rodzaj']
        for c,h in enumerate(heads,1):s.write(5,c,h,self.f['head'])
        self.calc_rows={}
        for ci,cr in enumerate(self.combo_rows):
            for m in range(7):
                r=6+ci*7+m;er=10+m*75;mr=17+m;rr=r+1;self.calc_rows[ci,m]=r
                self.formula(s,r,1,ref('KOMBINACJE',f'B{cr+1}'))
                s.write(r,2,m+1)
                self.formula(s,r,3,f'{ref("KOMBINACJE",f"K{cr+1}")}*{ref(mo,f"E{mr}")}*{ref(mo,"$M$7")}*{ref(me,"$B$1245")}')
                self.formula(s,r,4,ref('KOMBINACJE',f'{"L" if wall else "M"}{cr+1}'))
                # End forces and q in helper U:AI (12+3 values), combination coefficients D? table E:J.
                coeff=f"'KOMBINACJE'!$E${cr+1}:$J${cr+1}"
                for a in range(12):self.formula(s,r,21+a,f'SUMPRODUCT({ref(me,f"B{er+64+a}:G{er+64+a}")},{coeff})')
                for a in range(3):
                    vals=[ref(me,cell(er+25+c,1+a))+'*'+ref('KOMBINACJE',cell(cr,4+c)) for c in range(6)]
                    self.formula(s,r,33+a,'+'.join(vals))
                L=ref(me,cell(er+3,1));A=ref(me,cell(er+3,2));Iy=ref(me,cell(er+3,3));Iz=ref(me,cell(er+3,4))
                # positive internal N = tension; local end Fx_i reversed.
                self.formula(s,r,5,f'IF(D{rr}=0,0,MAX(0,-V{rr},-V{rr}-AH{rr}*{L}))')
                self.formula(s,r,6,f'IF(D{rr}=0,0,MAX(0,V{rr},V{rr}+AH{rr}*{L}))')
                # helpers xcrit_z for My and xcrit_y for Mz in AK, AL.
                self.formula(s,r,36,f'IF(AJ{rr}=0,0,MAX(0,MIN({L},-X{rr}/AJ{rr})))')
                self.formula(s,r,37,f'IF(AI{rr}=0,0,MAX(0,MIN({L},-W{rr}/AI{rr})))')
                # End moments My = Z, Mz = AA for start; internal values sign reversed.
                self.formula(s,r,7,f'IF(D{rr}=0,0,MAX(ABS(Z{rr}),ABS(-Z{rr}-X{rr}*{L}-AJ{rr}*{L}^2/2),ABS(-Z{rr}-X{rr}*AK{rr}-AJ{rr}*AK{rr}^2/2)))')
                self.formula(s,r,8,f'IF(D{rr}=0,0,MAX(ABS(AA{rr}),ABS(-AA{rr}+W{rr}*{L}+AI{rr}*{L}^2/2),ABS(-AA{rr}+W{rr}*AL{rr}+AI{rr}*AL{rr}^2/2)))')
                self.formula(s,r,9,f'IF(D{rr}=0,0,MAX(SQRT(W{rr}^2+X{rr}^2),SQRT((W{rr}+AI{rr}*{L})^2+(X{rr}+AJ{rr}*{L})^2)))')
                self.formula(s,r,10,f'IF(D{rr}=0,0,ABS(Y{rr}))')
                mat=ref(d,'$F$31')
                for c,idx in [(11,2),(12,3),(13,4)]:self.formula(s,r,c,f'IFERROR(E{rr}*VLOOKUP({mat},\'MATERIAŁY\'!$B$7:$J$9,{idx},FALSE)/\'MATERIAŁY\'!$G$24,0)')
                for c,f in [(14,f'F{rr}/{A}'),(15,f'G{rr}/{A}'),(16,f'H{rr}/({Iy}/({ref(mo,"G"+str(mr))}/2))'),(17,f'I{rr}/({Iz}/({ref(mo,"F"+str(mr))}/2))')]:self.formula(s,r,c,f'IF(D{rr}=0,0,{f})')
                self.formula(s,r,18,f'IF(D{rr}=0,0,MAX(O{rr}/M{rr}+Q{rr}/L{rr}+0.7*R{rr}/L{rr},O{rr}/M{rr}+0.7*Q{rr}/L{rr}+R{rr}/L{rr},(P{rr}/N{rr})^2+Q{rr}/L{rr}+0.7*R{rr}/L{rr},(P{rr}/N{rr})^2+0.7*Q{rr}/L{rr}+R{rr}/L{rr}))','percent')
                self.formula(s,r,20,ref('KOMBINACJE',f'C{cr+1}'))
                # Deflection: Hermite interpolation + exact uniform-load particular solution, 21 stations.
                # Only CHAR and SGU are displayed as displacement controls; SGN u is diagnostic.
                for sample in range(21):
                    t=sample/20;h1=1-3*t*t+2*t**3;h2=t-2*t*t+t**3;h3=3*t*t-2*t**3;h4=-t*t+t**3
                    comps=[]
                    for axis in range(3):
                        disp=[]
                        for a in range(12):
                            terms=[]
                            for case in range(6):
                                weight=ref('KOMBINACJE',cell(cr,4+case))
                                if ci==len(self.combo_rows)-1:
                                    kdef=f'INDEX(\'MATERIAŁY\'!$H$17:$H$19,{ref(d,"$F$32")})'
                                    psi2=ref('NORMY',{0:'G61',1:'G61',2:'G62',3:'G62',4:'G63',5:'G63'}[case])
                                    weight=f'({weight}+{kdef}*{("1" if case==0 else psi2)})' if case in [0,1,2] else '0'
                                terms.append(ref(me,cell(er+49+a,15+case))+'*'+weight)
                            disp.append('('+'+'.join(terms)+')')
                        # q_final must use same time-dependent weights as u_final.
                        qterms=[]
                        for case in range(6):
                            weight=ref('KOMBINACJE',cell(cr,4+case))
                            if ci==len(self.combo_rows)-1:
                                kdef=f'INDEX(\'MATERIAŁY\'!$H$17:$H$19,{ref(d,"$F$32")})'
                                psi2=ref('NORMY',{0:'G61',1:'G61',2:'G62',3:'G62',4:'G63',5:'G63'}[case])
                                weight=f'({weight}+{kdef}*{("1" if case==0 else psi2)})' if case in [0,1,2] else '0'
                            qterms.append(ref(me,cell(er+25+case,1+axis))+'*'+weight)
                        q='('+'+'.join(qterms)+')'
                        E=ref(mo,'H'+str(mr))
                        if axis==0:f=f'{1-t}*{disp[0]}+{t}*{disp[6]}+{q}*{L}^2*{t*(1-t)}/(2*{E}*{A})'
                        else:
                            ra=5 if axis==1 else 4;sign=1 if axis==1 else -1;I=Iz if axis==1 else Iy
                            f=f'{h1}*{disp[axis]}+{sign*h2}*{L}*{disp[ra]}+{h3}*{disp[axis+6]}+{sign*h4}*{L}*{disp[ra+6]}+{q}*{L}^4*{t*t*(1-t)*(1-t)}/(24*{E}*{I})'
                        target=42+sample*4+axis;self.formula(s,r,target,f'IF(D{rr}=0,0,{f})');comps.append(cell(r,target))
                    self.formula(s,r,42+sample*4+3,f'SQRT(SUMSQ({",".join(comps)}))')
                self.formula(s,r,19,f'IF(D{rr}=0,0,MAX({",".join(cell(r,45+sample*4) for sample in range(21))}))')
        s.conditional_format(6,18,187,18,{'type':'cell','criteria':'>','value':1,'format':self.f['fail']})
        s.conditional_format(6,18,187,18,{'type':'cell','criteria':'<=','value':1,'format':self.f['pass']})
        s.set_column('B:T',13);s.set_column('V:DV',11,None,{'hidden':True})
        s.print_area(0,0,187,20);s.repeat_rows(0,5)

    def results(self,code):
        wall=code=='A';s=self.s['ŚCIANA – WYNIKI' if wall else 'WYSUWNICA – WYNIKI'];ca='ŚCIANA – OBLICZENIA' if wall else 'WYSUWNICA – OBLICZENIA';me='MES '+code;d='ŚCIANA – DANE' if wall else 'WYSUWNICA – DANE'
        self.title(s,'ŚCIANA — WYNIKI' if wall else 'WYSUWNICA — WYNIKI','Wyniki charakterystyczne i aktywne kombinacje; wartości częściowe nie stanowią zatwierdzenia konstrukcji.')
        self.merge(s,5,1,5,'WYNIK OGÓLNY');self.merge(s,5,6,14,'=IF(COUNTIF(I12:I37,"NIE SPEŁNIA*")>0,"NIE SPEŁNIA","NIEZWERYFIKOWANE")','warn')
        self.merge(s,7,1,14,'Brak pełnego sprawdzenia przepony, poszycia, połączeń, kotew, wyboczenia, zwichrzenia, skręcania i II rzędu. Wynik pozytywny przekroju nie wystarcza.','warn');s.set_row(7,36)
        for c,h in enumerate(['ID','Typ','η przekrój max','Pręt krytyczny','u max mm','Limit mm','Kontrola u','Status cząstkowy'],1):s.write(10,c,h,self.f['head'])
        for ci,cr in enumerate(self.combo_rows):
            r=11+ci;start=7+ci*7;end=start+6;rr=r+1
            self.formula(s,r,1,ref('KOMBINACJE','B'+str(cr+1)))
            self.formula(s,r,2,ref('KOMBINACJE','C'+str(cr+1)))
            active='('+ref('KOMBINACJE','K'+str(cr+1))+'*'+ref('MODEL '+code,'$M$7')+'*'+ref(me,'$B$1245')+')'
            self.formula(s,r,3,f'IF({active}=0,"",MAX({ref(ca,f"S{start}:S{end}")}))','percent')
            self.formula(s,r,4,f'IF({active}=0,"",MATCH(D{rr},{ref(ca,f"S{start}:S{end}")},0))','auto')
            self.formula(s,r,5,f'IF({active}=0,"",MAX({ref(ca,f"T{start}:T{end}")}))','auto')
            self.formula(s,r,6,ref(d,'M40'),'auto')
            self.formula(s,r,7,f'IF(OR({active}=0,G{rr}<=0),"BRAK DANYCH",IF(F{rr}>G{rr},"PRZEKROCZENIE","KONTROLA CZĘŚCIOWA"))')
            self.formula(s,r,8,f'IF({active}=0,"NIEZWERYFIKOWANE",IF(AND(B{rr}<>"",C{rr}="SGN",D{rr}>1),"NIE SPEŁNIA — PRZEKRÓJ","NIEZWERYFIKOWANE"))')
        self.merge(s,32,1,14,'REAKCJE W PRZYPADKACH CHARAKTERYSTYCZNYCH — kN, MOMENTY kNm','section')
        for c,h in enumerate(['Przypadek','Węzeł','Rx','Ry','Rz','Mx','My','Mz'],1):s.write(34,c,h,self.f['head'])
        for case,name in enumerate(['G','S','W+','W−','H','Q']):
            for n in range(6):
                r=35+case*6+n;s.write(r,1,name);s.write(r,2,n+1)
                for axis in range(6):self.formula(s,r,3+axis,ref(me,cell(1200+n*6+axis,1+case))+f'/{1000 if axis<3 else 1000000}','auto')
        self.merge(s,73,1,14,'Reakcje są siłami PODPORY NA KONSTRUKCJĘ. Obciążenie mocowania ma przeciwny znak. Brak danych produktu = brak potwierdzenia nośności kotwy/łącznika.','warn');s.set_row(73,36)
        self.merge(s,76,1,14,'Ugięcie: maksimum normy wektora przemieszczeń w 21 punktach/pręt, względem układu globalnego, nie ugięcie względem cięciwy. Kontrola nie uwzględnia poślizgu złączy.','note');s.set_row(76,35)
        self.merge(s,79,1,14,'Siły końcowe dla każdej kombinacji: kolumny V:AG w OBLICZENIA (odkryj kolumny). Siły i reakcje kombinacji otrzymuje się liniowo z E:J w KOMBINACJE.','note');s.set_row(79,35)
        self.merge(s,83,1,14,'REAKCJE WSZYSTKICH KOMBINACJI — kN, kNm; OBCIĄŻENIE MOCOWANIA = −REAKCJA','section')
        for c,h in enumerate(['ID','Węzeł','Rx','Ry','Rz','Mx','My','Mz'],1):s.write(85,c,h,self.f['head'])
        for ci,cr in enumerate(self.combo_rows):
            active='('+ref('KOMBINACJE',f'K{cr+1}')+'*'+ref('MODEL '+code,'$M$7')+'*'+ref(me,'$B$1245')+')'
            for n in range(6):
                r=86+ci*6+n
                self.formula(s,r,1,ref('KOMBINACJE',f'B{cr+1}'));s.write(r,2,n+1)
                for axis in range(6):
                    row=1201+n*6+axis
                    self.formula(s,r,3+axis,f'IF({active}=0,"",SUMPRODUCT({ref(me,f"B{row}:G{row}")},{ref("KOMBINACJE",f"E{cr+1}:J{cr+1}")})/{1000 if axis<3 else 1000000})','auto')
        s.set_column('B:C',12);s.set_column('D:I',17);s.print_area(0,0,242,15);s.repeat_rows(0,3)

    def report(self):
        s=self.s['RAPORT'];self.title(s,'RAPORT OBLICZENIOWY — KONSTRUKCJE DREWNIANE','A4 • wyniki częściowe modelu liniowego 3D • nie jest kompletnym raportem zgodności z Eurokodami')
        for r,label,addr in [(5,'Inwestycja','G49'),(7,'Projekt','G51'),(9,'Data','G53')]:
            self.merge(s,r,1,5,label);self.merge(s,r,6,14,'='+ref('START',addr),'auto')
        self.merge(s,12,1,14,'WYNIK OGÓLNY: NIEZWERYFIKOWANE','warn')
        self.merge(s,14,1,14,'Model: 6 węzłów, 7 prętów, sztywne węzły. Podpory translacyjne i rotacyjne określone w MODEL A/B. Brak II rzędu, podatności połączeń, poszycia i przepon.','note');s.set_row(14,38)
        for row,code,d in [(18,'A','ŚCIANA – DANE'),(31,'B','WYSUWNICA – DANE')]:
            self.merge(s,row,1,14,'MODUŁ '+code+' — '+('ŚCIANA' if code=='A' else 'WYSUWNICA'),'section')
            labels=[('Geometria / schemat','F21'),('Wymiar 1 [mm]','F23'),('Wymiar 2 [mm]','F25'),('Drewno','F31'),('b [mm]','M31'),('h [mm]','M32'),('G [kN/m²]','F36'),('S [kN/m² rzutu]','F38'),('W+ [kN/m²]','F40'),('W− [kN/m²]','F42')]
            for i,(label,a) in enumerate(labels):self.merge(s,row+1+i,1,7,label);self.merge(s,row+1+i,8,14,'='+ref(d,a),'auto')
        self.merge(s,45,1,14,'PODSTAWA I OGRANICZENIA','section')
        self.merge(s,47,1,14,'PN-EN 1995-1-1:2010 z zawartym NA i PN-EN 338:1999 — wydania historyczne, aktualność niepotwierdzona. Współczynniki PN-EN 1990 wymagają danych użytkownika (NORMY).','warn');s.set_row(47,42)
        self.merge(s,50,1,14,'Ku=F; R=Ku−F; σ=N/A; σm=M/W; Xd=kmod·Xk/γM. Dokładne macierze, obciążenia i siły prętów są jawne w MES i OBLICZENIA. Maksima naprężeń mogą pochodzić z różnych przekrojów (konserwatywna obwiednia).','note');s.set_row(50,42)
        self.merge(s,53,1,14,'WYNIKI SGN I SGU — PODSUMOWANIE','section')
        for r,ca in [(55,'ŚCIANA – WYNIKI'),(58,'WYSUWNICA – WYNIKI')]:
            self.merge(s,r,1,5,ca)
            self.merge(s,r,6,14,'='+ref(ca,'G6'),'warn')
            self.merge(s,r+1,1,14,'Pełne tablice przypadków, przemieszczeń i reakcji: '+ca+'. Do wydruku dołącz arkusze DANE, MODEL, KOMBINACJE, OBLICZENIA i WYNIKI.','note');s.set_row(r+1,30)
        self.merge(s,61,1,14,'Kontrola projektanta: potwierdzić aktualny zestaw norm, warunki stosowalności, rzeczywiste podpory i sztywności złączy, stateczność, poszycie, kotwy i nośności producenta.','warn');s.set_row(61,40)
        self.merge(s,65,1,14,'WYNIKI LICZBOWE — UZUPEŁNIAJĄCE','section')
        for row,ca in [(67,'ŚCIANA – WYNIKI'),(78,'WYSUWNICA – WYNIKI')]:
            self.merge(s,row,1,14,ca,'section')
            values=[('Maks. η przekroju CHAR (diagnostyczne)',f'MAX({ref(ca,"D12:D17")})'),
                    ('Maks. η przekroju SGN',f'IF(COUNT({ref(ca,"D18:D35")})=0,"BRAK DANYCH",MAX({ref(ca,"D18:D35")}))'),
                    ('Przemieszczenie SGU char [mm]',ref(ca,'F36')),
                    ('Przemieszczenie SGU final [mm]',ref(ca,'F37')),
                    ('Wymagana siła na wyrywanie SGN [kN]',f'IF(COUNT({ref(ca,"F123:F230")})=0,"BRAK DANYCH",MAX(0,-MIN({ref(ca,"F123:F230")})))'),
                    ('Wynik ogólny',ref(ca,'G6'))]
            for i,(label,f) in enumerate(values):
                self.merge(s,row+1+i,1,8,label)
                self.merge(s,row+1+i,9,14,'='+f,'auto')
        s.set_portrait();s.fit_to_pages(1,0);s.set_h_pagebreaks([45]);s.print_area(0,0,86,15)

    def tests(self):
        s=self.s['TESTY'];self.title(s,'TESTY I WALIDACJA','Nie utożsamiać testów mechaniki ramy z certyfikacją normową. Wyniki rzeczywistych testów w tests/results.json i docs/TESTY.md.')
        self.merge(s,6,1,14,'Kontrole wykonywane na bieżąco w Excelu (siły w N, momenty Nmm)','section')
        for c,h in enumerate(['Model','Przypadek','ΣFx + Rx','ΣFy + Ry','ΣFz + Rz','max reszta wolnych DOF','Kontrola sił'],1):s.write(8,c,h,self.f['head'])
        r=9
        for code in 'AB':
            me='MES '+code
            for case in range(6):
                cc=col(1+case);s.write(r,1,code);s.write(r,2,['G','S','W+','W−','H','Q'][case])
                for axis in range(3):
                    terms=[ref(me,f'{cc}{801+n*6+axis}')+'+'+ref(me,f'{cc}{1201+n*6+axis}') for n in range(6)]
                    self.formula(s,r,3+axis,'+'.join(terms),'auto')
                terms=[f'ABS({ref(me,f"{cc}{1201+i}")})*(1-{ref(me,f"AN{601+i}")})' for i in range(36)]
                self.formula(s,r,6,'MAX('+','.join(terms)+')','auto')
                self.formula(s,r,7,f'IF(OR({ref("MODEL "+code,"$M$7")}=0,{ref(me,"$B$1245")}=0),"BRAK DANYCH / MECHANIZM",IF(MAX(ABS(D{r+1}),ABS(E{r+1}),ABS(F{r+1}),G{r+1})<0.001,"OK","BŁĄD / MECHANIZM"))')
                r+=1
        self.merge(s,24,1,14,'Ta tabela bada sumę sił i resztę równań. Testy niezależne obejmują również globalne momenty, macierze, ugięcia i reakcje z analitycznych wzorców oraz modyfikacje pliku.','note');s.set_row(24,42)
        self.merge(s,28,1,14,'Normowe przykłady przepon, kotew, płytek, zwichrzenia i II rzędu: NIEWYKONANE — funkcje niezaimplementowane. Otwarcie w Microsoft Excel 365: nie testowano w tym środowisku; przeliczono w LibreOffice.','warn');s.set_row(28,42)
        s.print_area(0,0,31,15)


if __name__ == '__main__':
    OUT.parent.mkdir(parents=True,exist_ok=True)
    Builder(Path(sys.argv[1]) if len(sys.argv)>1 else OUT)
    print(OUT)
