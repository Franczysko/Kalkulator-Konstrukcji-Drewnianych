from pathlib import Path
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
out=Path('/tmp/timber-variants');out.mkdir(exist_ok=True)
source=ROOT/'output/Kalkulator_konstrukcji_drewnianych.xlsx'
for name in ['triangle','changed_geometry','overload','missing','mechanism']:
 w=load_workbook(source);a=w['ŚCIANA – DANE'];b=w['WYSUWNICA – DANE']
 if name=='triangle':
  for c,v in {'F21':'Szczyt','F23':2400,'F25':0,'F27':1200,'F29':0}.items():a[c]=v
 elif name=='changed_geometry':
  for c,v in {'F21':'Trapez','F23':1800,'F25':2000,'F29':2600,'M25':'45×195','F40':1.2}.items():a[c]=v
  for c,v in {'F23':900,'F25':1500,'F27':1800,'F29':40,'M25':'45×170'}.items():b[c]=v
  w['OBCIĄŻENIA B']['F49']=2.0 # additional point force in global Z, Q at node 1
 elif name=='overload':
  n=w['NORMY']
  for r,v in enumerate([1.2,.8,1.4,.3,.4,.5,.1,.1,.1],55):n[f'G{r}']=v
  n['G65']='WYŁĄCZNIE TEST — współczynniki syntetyczne, nie normowe';n['G67']='TAK'
  for row in range(7,10):
   for col in ['C','D','E']:w['MATERIAŁY'][f'{col}{row}']=.001
 elif name=='missing':a['F23']=None
 elif name=='mechanism':
  for code in 'AB':
   for row in range(7,13):
    for col in range(6,12):w['MODEL '+code].cell(row,col,0)
 w.save(out/(name+'.xlsx'))
 print(out/(name+'.xlsx'))
