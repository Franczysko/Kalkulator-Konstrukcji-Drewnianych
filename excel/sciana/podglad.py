"""Eksport widocznych kart do kontroli wyglądu; plik dostarczany pozostaje bez zmian."""
from pathlib import Path
import os,sys,tempfile,subprocess
from openpyxl import load_workbook
import fitz

def render(source,destination,label):
 out=Path(destination);out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='sciana-pdf-') as tmp:
  root=Path(tmp);w=load_workbook(source)
  for s in w:
   if s.title not in ['DANE WEJŚCIOWE','ŚCIANA SZCZYTOWA']:s.print_area='A1:A1'
  p=root/'preview.xlsx';w.save(p)
  profile=root/'profile';(profile/'user').mkdir(parents=True)
  (profile/'user/registrymodifications.xcu').write_text('''<oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item></oor:items>''')
  subprocess.run([os.environ.get('LO_BIN','libreoffice'),'-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','pdf','--outdir',str(root),str(p)],check=True,timeout=180)
  pdf=fitz.open(root/'preview.pdf');pages=[]
  for i,page in enumerate(pdf):
   if 'Ściana szczytowa — schemat i wyniki' in page.get_text():
    page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(out/(label+'.png'));pages.append(i)
  assert pages, 'Brak strony z kartą ściany'
  if label=='dane_i_trojkat':
   result=fitz.open();result.insert_pdf(pdf,from_page=0,to_page=pages[0]);result.save(out/'Dane_i_schemat_podglad.pdf')

if __name__=='__main__':render(*sys.argv[1:])
