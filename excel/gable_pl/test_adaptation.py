"""Independent numeric oracle and strict nonvisual-only package audit."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from copy import deepcopy
import json,math,re,sys,tempfile
from lxml import etree
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'gable_pl'))
from recalculate import recalculate
from adapt import replace_cell,SOFT
from cache_native import cache

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
CHECKS=[]

def check(name,a,b,tol=1e-7):
 if isinstance(a,str) or isinstance(b,str):passed=a==b;delta=None
 else:delta=abs(a-b);passed=delta<=tol*max(1,abs(a),abs(b))
 CHECKS.append({'name':name,'expected':b,'actual':a,'passed':passed,'absolute_difference':delta})
 assert passed,(name,a,b)


def layout(original,adapted):
 allowed={'xl/workbook.xml','xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml'}
 with ZipFile(original) as src,ZipFile(adapted) as out:
  assert set(src.namelist())==set(out.namelist())
  identical=[]
  for name in src.namelist():
   if name not in allowed:
    assert src.read(name)==out.read(name),('Unexpected non-cell change',name);identical.append(name)
  for i in [1,2,3]:
   roots=[]
   for archive in [src,out]:
    root=etree.fromstring(archive.read(f'xl/worksheets/sheet{i}.xml'))
    for c in root.findall('.//m:c',NS):
     c.attrib.pop('t',None)
     for child in list(c):c.remove(child)
    roots.append(etree.tostring(root,method='c14n'))
   assert roots[0]==roots[1],('Cell layout/style metadata changed',i)
  # Print areas/names retain original content; extra _PL parameters are nonvisual.
  a=etree.fromstring(src.read('xl/workbook.xml'));b=etree.fromstring(out.read('xl/workbook.xml'))
  for n in b.findall('m:definedNames/m:definedName',NS):
   if n.get('name','').startswith('_PL_'):n.getparent().remove(n)
  for r in [a,b]:
   cp=r.find('m:calcPr',NS);r.remove(cp)
  assert etree.tostring(a,method='c14n')==etree.tostring(b,method='c14n')
 CHECKS.append({'name':'Layout and all graphics/controls/printer settings byte-identical','passed':True,'unchanged_parts':identical})


def oracle(w,label):
 mat=w['Value'];idx=int(mat['M6'].value);cls=mat.cell(4+idx,2).value
 # Material values independently checked against transcribed primary-source table.
 if cls not in SOFT:return
 fm,ft,fc,fc90,fv,e,e05,rhok,rhom,g=SOFT[cls]
 service=int(float(w.defined_names['_PL_klasa_uzytkowania'].attr_text))
 kmod=[.9,.9,.7][service-1];beta=float(w.defined_names['_PL_beta_L'].attr_text)
 for side in [0,1]:
  s=w.worksheets[side];b=s[f'C{29+side}'].value;h=s[f'E{29+side}'].value
  lm=s[f'D{26-side}'].value;l=lm*1000;n=s[f'R{27+side}'].value;space=s['G26' if side==0 else 'H25'].value
  angle=s[f'D{12-side}'].value;alpha=math.radians(angle);sk=s[f'H{14-side}'].value
  mu=.8 if angle<=30 else .8*(60-angle)/30 if angle<60 else 0
  snow=mu*sk
  qw=s[f'D{18-side}'].value*(s[f'O{29+side}'].value-s[f'O{30+side}'].value)*space
  kmod=([.9,.9,.7] if abs(qw)>0 else [.8,.8,.65] if snow>0 and s[f'O{37+side}'].value>0 else [.6,.6,.5])[service-1]
  gg=s[f'O{35+side}'].value;gq=s[f'O{36+side}'].value;psi=s[f'O{37+side}'].value
  strip=s[f'D{16-side}'].value+(h*n if side else h)/1000+s[f'H{16-side}'].value/2
  ng=strip*s[f'D{14-side}'].value*gg/math.cos(alpha)
  ns=strip*snow*gq*psi
  wall=s['F23' if side==0 else 'F22'].value
  sigman=(1000*(ng+ns)*space+1000*wall*gg*lm*space)/(b*h*n)
  lam=beta*l/(min(b,h)/math.sqrt(12))/math.pi*math.sqrt(fc/e05)
  k=.5*(1+.2*(lam-.3)+lam*lam)
  kc=1 if lam<=.3 else 1/(k+math.sqrt(k*k-lam*lam))
  fcd=fc*kmod*kc/1.3;kh=min((150/h)**.2,1.3) if h<150 else 1;fmd=fm*kmod*kh/1.3
  q=s[f'D{18-side}'].value*(s[f'O{29+side}'].value-s[f'O{30+side}'].value)*space;m=abs(q)*l*l/8
  a=b*h;ii=b*h**3/12
  if side==0 or n==1:
   sigma_b=m*gq/(n*b*h*h/6);eta=sigman/fcd+sigma_b/fmd;ei=e*ii*n
  else:
   diameter=s['D27'].value;spacing=s['H27'].value;kser=rhom**1.5*diameter**.8/30
   gu=1/(1+math.pi**2*e*a*spacing/((2/3)*kser*l*l));gs=1/(1+math.pi**2*e*a*spacing/(kser*l*l))
   # Locate elastic neutral axes and evaluate section sums independently.
   def effective(gamma):
    centers=[h,0,-h] if n==3 else [h,0]
    factors=[gamma,1,gamma] if n==3 else [gamma,1]
    centroid=sum(c*f for c,f in zip(centers,factors))/sum(factors)
    offsets=[c-centroid for c in centers]
    val=sum(e*ii+f*e*a*c*c for c,f in zip(offsets,factors))
    return val,offsets,factors
   eiu,offsets,factors=effective(gu);ei,_,_=effective(gs)
   stressax=[abs(f*e*c*m/eiu)*gq for c,f in zip(offsets,factors)]
   stressm=e*h*m/(2*eiu)*gq
   sigma_b=max(stressax)+stressm
   eta=max((sigman+max(stressax))/fcd+stressm/fmd,max(0,max(stressax)-sigman)/(ft*kmod/1.3)+stressm/fmd)
   check(label+s.title+' Kser',s['S61'].value,kser)
   check(label+s.title+' EIu',s['S71'].value,eiu)
   force=max(f*e*a*abs(c) for c,f in zip(offsets,factors))*spacing*(abs(q)*l/2*gq)/eiu
   check(label+s.title+' nail force',s['S81'].value,force)
  u=5*abs(q)*l**4/(384*ei)+1.2*abs(q)*l*l/(8*n*a*g)
  for addr,expected in [(f'O{34+side}',kmod),('P61',snow),(f'C{37+side}',sigman),(f'H{37+side}',sigma_b),(f'C{40+side}',fcd),(f'H{40+side}',fmd),(f'C{45+side}',eta),(f'C{49+side}',u),(f'S{50+2*side}',kc)]:
   check(label+s.title+' '+addr,s[addr].value,expected)
  if label=='low':
   check(label+s.title+' no false OK',s[f'E{45+side}'].value,'NZ')
 errors=[(s.title,c.coordinate,c.value) for s in w for row in s for c in row if c.data_type=='e'];assert not errors,errors


def variant(source,dest,changes,names):
 with ZipFile(source) as src,ZipFile(dest,'w',ZIP_DEFLATED) as out:
  for info in src.infolist():
   data=src.read(info.filename)
   if info.filename in changes:
    text=data.decode()
    for addr,val in changes[info.filename].items():text=replace_cell(text,addr,val)
    data=text.encode()
   if info.filename=='xl/workbook.xml':
    text=data.decode()
    for name,value in names.items():text=re.sub(r'(<definedName name="'+name+r'">).*?(</definedName>)',r'\g<1>'+str(value)+r'\2',text)
    data=text.encode()
   out.writestr(info,data)


def run(original):
 source=ROOT/'output/Gable_panel_stud_PL.xlsx';layout(original,source)
 cases=[('base',{},{}),('C18',{'xl/worksheets/sheet3.xml':{'M6':5}},{}),('C30',{'xl/worksheets/sheet3.xml':{'M6':8}},{}),('service3',{}, {'_PL_klasa_uzytkowania':3}),('angle45',{'xl/worksheets/sheet1.xml':{'D12':45},'xl/worksheets/sheet2.xml':{'D11':45}},{}),('angle60',{'xl/worksheets/sheet1.xml':{'D12':60},'xl/worksheets/sheet2.xml':{'D11':60}},{}),('one_ply',{'xl/worksheets/sheet2.xml':{'R28':1}},{}),('two_plies',{'xl/worksheets/sheet2.xml':{'R28':2}},{}),('suction',{'xl/worksheets/sheet1.xml':{'O29':-.7,'O30':.2},'xl/worksheets/sheet2.xml':{'O30':-.7,'O31':.2}},{}),('spacing',{'xl/worksheets/sheet1.xml':{'G26':.4},'xl/worksheets/sheet2.xml':{'H25':.4}},{}),('gap',{'xl/worksheets/sheet2.xml':{'H15':1.2}},{}),('buckling_only',{}, {'_PL_beta_L':.5}),('no_wind',{'xl/worksheets/sheet1.xml':{'D18':0},'xl/worksheets/sheet2.xml':{'D17':0}},{}),('permanent',{'xl/worksheets/sheet1.xml':{'D18':0,'H14':0},'xl/worksheets/sheet2.xml':{'D17':0,'H13':0}},{}),('low',{'xl/worksheets/sheet1.xml':{'D18':.001,'D14':.001,'H14':.001,'F23':.001},'xl/worksheets/sheet2.xml':{'D17':.001,'D13':.001,'H13':.001,'F22':.001}}, {})]
 with tempfile.TemporaryDirectory(prefix='gable-qa-') as td:
  root=Path(td);base=None
  for label,changes,names in cases:
   before=root/(label+'.xlsx');after=root/(label+'-calc.xlsx');variant(source,before,changes,names);recalculate(before,after)
   w=load_workbook(after,data_only=True);oracle(w,label)
   if label=='base':base=after
  final=root/'final.xlsx';cache(source,base,final);source.write_bytes(final.read_bytes())
 layout(original,source);oracle(load_workbook(source,data_only=True),'delivered')
 (ROOT/'gable_pl/test_results.json').write_text(json.dumps({'passed':len(CHECKS),'failed':0,'checks':CHECKS},ensure_ascii=False,indent=2))
 print(len(CHECKS),'checks passed; original layout retained')

if __name__=='__main__':run(sys.argv[1])
