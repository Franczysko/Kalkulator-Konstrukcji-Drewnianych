"""Rzeczywiste przeliczenia czterech kształtów i niezależna kontrola mechaniki."""
from pathlib import Path
import json
import sys
import tempfile
import numpy as np
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recalculate import recalculate
from frame import solve
from cache import inject

checks=[]
def close(name,actual,expected,atol=1e-5,rtol=2e-7):
 a=np.asarray(actual,float);e=np.asarray(expected,float)
 assert np.allclose(a,e,atol=atol,rtol=rtol),(name,float(np.max(np.abs(a-e))))
 checks.append({'test':name,'passed':True,'maximum_absolute_difference':float(np.max(np.abs(a-e))),'atol':atol,'rtol':rtol})

def verify(path,label,expected_heights=None):
 w=load_workbook(path,data_only=True);d=w['DANE WEJŚCIOWE'];wall=w['ŚCIANA – DANE'];calc=w['ŚCIANA – OBLICZENIA'];mat=w['A – MACIERZE']
 errors=[(s.title,c.coordinate,c.value) for s in w for row in s for c in row if c.data_type=='e']
 assert not errors,(label,errors[:10]);checks.append({'test':label+': brak błędów Excel','passed':True})
 assert all(s.sheet_state=='hidden' for s in w if s.title.startswith('WYSUWNICA') or s.title=='B – MACIERZE')
 assert w.sheetnames[0]=='DANE WEJŚCIOWE'
 for sn in ['DANE WEJŚCIOWE','ŚCIANA SZCZYTOWA']:
  assert all(ser.smooth is False for ser in w[sn]._charts[0].series), (sn,'odcinki muszą być proste')
  assert w[sn]._charts[0].visible_cells_only is False, (sn,'wykres musi rysować również ukryte komórki pomocnicze')
 assert all(w['ŚCIANA SZCZYTOWA'][a].data_type!='e' for a in ['C6','F6','I6','C29','F29','I29'])
 if expected_heights is not None:close(label+': wysokości słupków',[wall[f'C{r}'].value for r in [20,21,22]],expected_heights)
 if label=='brak_szerokosci':
  assert d['F60'].value!='OK' and w['ŚCIANA – WYNIKI']['B12'].value!='OK MECHANIKA'
  return
 if label=='wiatr_snieg':
  close('w=qp(cpe-cpi), parcie',d['F21'].value,800)
  close('w=qp(cpe-cpi), ssanie',d['F22'].value,640)
  close('s=mu*Ce*Ct*sk',d['F35'].value,792)
 if label=='drewno_C18':close('C18: E/G/rho',[d[f'F{r}'].value for r in [87,88,89]],[9000,560,380])
 assert w['ŚCIANA – WYNIKI']['B12'].value=='OK MECHANIKA',(label,w['ŚCIANA – WYNIKI']['B12'].value)
 nodes=np.array([[wall.cell(17+n,2+a).value for a in range(3)] for n in range(6)],float)
 supports=np.array([[wall.cell(26+n,2+a).value for a in range(6)] for n in range(6)],int)
 members=[(int(wall.cell(76+m,2).value)-1,int(wall.cell(76+m,3).value)-1,int(wall.cell(76+m,10).value)) for m in range(7)]
 props=np.array([[wall.cell(76+m,4+a).value for a in range(4)] for m in range(7)],float)
 heights=nodes[3:,1];area=d['F50'].value/4*(heights[0]+2*heights[1]+heights[2])/1e6
 for case,name in enumerate(['G','S','W+','W−','Q','DOD']):
  line=np.array([[wall.cell(86+case*7+m,3+a).value for a in range(3)] for m in range(7)],float)
  nodal=np.array([[wall.cell(36+case*6+n,2+a).value*(1000 if a<3 else 1e6) for a in range(6)] for n in range(6)],float)
  u,reactions,forces,k,f=solve(nodes,members,supports,props,line,nodal)
  close(label+name+': 36 DOF',[calc.cell(5+i,8+case).value for i in range(36)],u)
  close(label+name+': 36 reakcji',[calc.cell(44+i,2+case).value for i in range(36)],reactions,atol=.01)
  close(label+name+': macierz 36x36',[[mat.cell(487+i,2+j).value for j in range(36)] for i in range(36)],k,atol=.1)
  total=(reactions+f).reshape(6,6)
  close(label+name+': rownowaga sil',total[:,:3].sum(axis=0),np.zeros(3))
  close(label+name+': rownowaga momentow',(total[:,3:]+np.cross(nodes,total[:,:3])).sum(axis=0),np.zeros(3),atol=.02)
  if case in [2,3]:close(label+name+': pole sciany a suma wiatru',f.reshape(6,6)[:,2].sum(),(1 if case==2 else -1)*d[f'F{21 if case==2 else 22}'].value*area+nodal[:,2].sum())
 assert w['ŚCIANA – WYNIKI']['B5'].value!='SPEŁNIA'


def run():
 source=ROOT/'output/Sciana_Szczytowa_PL.xlsx'
 with tempfile.TemporaryDirectory(prefix='sciana-test-') as tmp:
  root=Path(tmp)
  cases=[('trojkat','Szczytowa – trójkąt',[0,3000,0]),('prostokat','Prostokąt',[3000,3000,3000]),('jednospadowa','Szczytowa jednospadowa',[0,1500,3000]),('kolankowa','Szczytowa ze ścianką kolankową',[1000,3000,1000]),('wiatr_snieg','Szczytowa – trójkąt',[0,3000,0]),('drewno_C18','Prostokąt',[3000,3000,3000]),('brak_szerokosci','Szczytowa – trójkąt',None)]
  baseline=None
  for label,shape,heights in cases:
   w=load_workbook(source);d=w['DANE WEJŚCIOWE'];d['F49']=shape
   if label=='kolankowa':d['F54']=1000
   if label=='wiatr_snieg':
    for a,v in {'F7':'qp i współczynniki','F13':800,'F14':.8,'F15':-.6,'F16':-.2,'F17':.2,'F27':'μ·Ce·Ct·sk','F30':900,'F31':1.1,'F32':1,'F33':.8}.items():d[a]=v
   if label=='drewno_C18':d['F84']='C18'
   if label=='brak_szerokosci':d['F50']=None
   before=root/(label+'.xlsx');after=root/(label+'-calc.xlsx');w.save(before)
   recalculate(before,after);verify(after,label,heights)
   if label in ['trojkat','prostokat','jednospadowa','kolankowa']:
    ui=Path('/tmp/sciana-ui');ui.mkdir(exist_ok=True);(ui/(label+'.xlsx')).write_bytes(after.read_bytes())
   if label=='trojkat':baseline=after
  final=root/'final.xlsx';inject(source,baseline,final);source.write_bytes(final.read_bytes());verify(source,'dostarczony',[0,3000,0])
 (ROOT/'sciana/wyniki_testow.json').write_text(json.dumps({'passed':len(checks),'failed':0,'checks':checks},ensure_ascii=False,indent=2))
 print(len(checks),'kontroli zaliczonych')

if __name__=='__main__':run()
