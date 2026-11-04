"""Adapt only cell contents and calculation metadata; preserve original XLSX graphics/layout verbatim."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import re
import sys
from package_fix import clean_calc_chain

ROOT=Path(__file__).resolve().parents[1]
SOFT={
 'C14':[14,8,16,4.3,1.7,7000,4700,290,350,440],
 'C16':[16,10,17,4.6,1.8,8000,5400,310,370,500],
 'C18':[18,11,18,4.8,2,9000,6000,320,380,560],
 'C22':[22,13,20,5.1,2.4,10000,6700,340,410,630],
 'C24':[24,14,21,5.3,2.5,11000,7400,350,420,690],
 'C27':[27,16,22,5.6,2.8,12000,8000,370,450,750],
 'C30':[30,18,23,5.7,3,12000,8000,380,460,750],
 'C35':[35,21,25,6,3.4,13000,8700,400,480,810],
 'C40':[40,24,26,6.3,3.8,14000,9400,420,500,880],
}
PARAMS={
 '_PL_klasa_uzytkowania':2,
 '_PL_Ce':1,
 '_PL_Ct':1,
 '_PL_beta_L':1,
 '_PL_ksys':1,
 '_PL_limit_ratio':0.0045,
 '_PL_kombinacje_potwierdzone':0,
 '_PL_wiatr_potwierdzony':0,
 '_PL_snieg_potwierdzony':0,
 '_PL_schemat_potwierdzony':0,
 '_PL_limit_potwierdzony':0,
 '_PL_polaczenie_potwierdzone':0,
 '_PL_Flacznika_Rd_N':0,
}


def replace_cell(xml,address,value,cache=None):
 pattern=re.compile(r'<c\b(?=[^>]*\br="'+re.escape(address)+r'")[^>]*?(?:/>|>.*?</c>)',re.S)
 match=pattern.search(xml)
 if not match:
  # Fill only an existing row; no layout rows/columns or styles are created.
  rownum=re.search(r'\d+',address).group(0)
  rowmatch=re.search(r'<row\b(?=[^>]*\br="'+rownum+r'")[^>]*>.*?</row>',xml,re.S)
  if not rowmatch:raise ValueError('Expected existing row: '+rownum)
  temporary='<c r="'+address+'"/>'
  insert=rowmatch.end()-len('</row>')
  xml=xml[:insert]+temporary+xml[insert:]
  match=pattern.search(xml)

 opening=match.group(0).split('>')[0].rstrip('/')+'>'
 opening=re.sub(r'\s+t="[^"]*"','',opening)
 if isinstance(value,str) and value.startswith('='):
  body='<f>'+escape(value[1:])+'</f><v>'+escape(str(0 if cache is None else cache))+'</v>'
 elif isinstance(value,str):
  opening=opening[:-1]+' t="inlineStr">';body='<is><t>'+escape(value)+'</t></is>'
 elif value is None:body=''
 else:body='<v>'+str(value)+'</v>'
 return xml[:match.start()]+opening+body+'</c>'+xml[match.end():]


def formulas():
 flat={};edge={};value={}
 # Only reference classes positively read from PN-EN 338:1999 table 1.
 rows={5:'C16',6:'C24',8:'C14',9:'C18',10:'C22',11:'C27',12:'C30',13:'C35',14:'C40'}
 for row,cls in rows.items():
  fm,ft,fc,fc90,fv,e,e05,rhok,rhom,g=SOFT[cls]
  for column,number in zip(['C','D','E','F','G','H','I','J','K','L'],[fm,ft,fc,fc90,fc90,fv,e,e05,rhok,rhom]):value[column+str(row)]=number
 value['M6']=2 # Existing C24 row; no verified TR26 product declaration supplied.
 eligible='OR(Value!$M$6=1,Value!$M$6=2,AND(Value!$M$6>=4,Value!$M$6<=10))'
 for target,offset,depth,width,span,spacing,wind,sgnrow,defrow in [(flat,0,'E29','C29','D26','G26','D18',45,49),(edge,1,'E30','C30','D25','H25','D17',46,50)]:
  target['O'+str(34+offset)]=f'=IF(ABS(S{31+2*offset})>0,CHOOSE(_PL_klasa_uzytkowania,0.9,0.9,0.7),IF(AND(P61>0,O{37+offset}>0),CHOOSE(_PL_klasa_uzytkowania,0.8,0.8,0.65),CHOOSE(_PL_klasa_uzytkowania,0.6,0.6,0.5)))'
  target['O'+str(33+offset)]=1.3
  # Remove the undocumented 0.85L reduction; this is a two-end-supported member assumption.
  le='S'+str(44+2*offset);i='S'+str(46+2*offset);rel='S'+str(48+2*offset);k='S'+str(49+2*offset);kc='S'+str(50+2*offset)
  target[le]=f'={span}*1000*_PL_beta_L'
  target[i]=f'=MIN({width},{depth})/SQRT(12)'
  target[kc]=f'=IF({rel}<=0.3,1,MIN(1,1/({k}+SQRT(MAX(0,{k}^2-{rel}^2)))))'
  target['P60']=0 # Remove the unsupported UK minimum roof snow of 0.6 kN/m2.
  angle='D'+str(12-offset);snow='H'+str(14-offset)
  target['P59']=f'=IF({angle}<=30,0.8,IF({angle}<60,0.8*(60-{angle})/30,0))*_PL_Ce*_PL_Ct*{snow}'
  target['P61']='=P59'
  ratio='C'+str(sgnrow)
  prerequisites=f'AND({eligible},_PL_kombinacje_potwierdzone=1,_PL_wiatr_potwierdzony=1,_PL_snieg_potwierdzony=1,_PL_schemat_potwierdzony=1)'
  connection='' if offset==0 else ',OR(R28=1,AND(_PL_polaczenie_potwierdzone=1,_PL_Flacznika_Rd_N>0,S81<=_PL_Flacznika_Rd_N))'
  if offset==0:prerequisites=f'AND({prerequisites},R27=1)'
  else:prerequisites=f'AND({prerequisites}{connection})'
  target['E'+str(sgnrow)]=f'=IFERROR(IF(NOT({eligible}),"NZ",IF({ratio}>1,"FAIL",IF({prerequisites},"OK","NZ"))),"NZ")'
  target['F'+str(defrow)]=f'=_PL_limit_ratio*{span}*1000'
  target['H'+str(defrow)]=f'=IFERROR(IF(NOT({eligible}),"NZ",IF(C{defrow}>F{defrow},"FAIL",IF(AND(_PL_limit_potwierdzony=1,_PL_schemat_potwierdzony=1,_PL_wiatr_potwierdzony=1),"OK","NZ"))),"NZ")'
 # Axial force: roof line load kN/m must be multiplied by the stud spacing in m.
 flat['C37']='=IFERROR((1000*(O44+O45)*G26+1000*F23*O35*D26*G26)/(C29*E29*R27),"NZ")'
 flat['S32']='=ABS(S31)*(D26*1000)^2/8'
 flat['C45']='=IFERROR(H37/H40+C37/C40,"NZ")'
 flat['H37']='=IFERROR(ABS(S32*O36/S29),"NZ")'
 flat['C40']='=IFERROR(S37*_PL_ksys*O34*S50/O33,"NZ")'
 flat['H40']='=IFERROR(S36*_PL_ksys*S34*O34/O33,"NZ")'
 flat['S40']='=IFERROR(CHOOSE(Value!$M$6,500,690,0,440,560,630,750,750,810,880),0)'
 flat['C49']='=IFERROR(5*ABS(S31)*(D26*1000)^4/(384*S38*S30)+1.2*ABS(S31)*(D26*1000)^2/(8*S33*S40),"NZ")'
 flat['A33']='PL NA.1: short-term wind action; confirm external and internal wind coefficients.'
 flat['A34']='NZ = unverified assumptions; scope and missing PN-EN 1990/NA: see documentation.'
 flat['A52']='Deflection limit is a project assumption, not a verified PL limit for studs.'
 flat['B42']='kc,min'
 edge['S34']='=ABS(S33)*(D25*1000)^2/8'
 edge['C38']='=IFERROR((1000*(O45+O46)*H25+1000*F22*O36*D25*H25)/(C30*E30*R28),"NZ")'
 edge['C41']='=IFERROR(S39*_PL_ksys*O35*S52/O34,"NZ")'
 edge['H41']='=IFERROR(S38*_PL_ksys*S44*O35/O34,"NZ")'
 edge['S42']='=IFERROR(CHOOSE(Value!$M$6,500,690,0,440,560,630,750,750,810,880),0)'
 edge['S43']='=INDEX(Value!$L$5:$L$20,Value!$M$6)'
 edge['O46']='=(D15+E30*R28/1000+H15/2)*P61*O37*O38' # H16 is not the distance input; H15 is the correct reference.
 edge['S62']='=1/(1+PI()^2*S40*S36*H27/((2/3)*S61*(D25*1000)^2))'
 edge['S64']='=IF(R28=3,1/(1+PI()^2*S40*S37*H27/((2/3)*S61*(D25*1000)^2)),0)'
 edge['S65']='=(S62*S40*S36*2*E30-S64*S40*S37*2*E30)/(2*(S62*S40*S36+S63*S40*S36+S64*S40*S37))'
 edge['S70']='=S40*S32+S64*S40*S37*S67^2'
 edge['H38']='=IFERROR(IF(R28=1,ABS(S34*O37/S30),MAX(ABS(S73)+ABS(S76),ABS(S74)+ABS(S77),ABS(S75)+ABS(S78))*O37),"NZ")'
 # Annex B: axial stress induced by composite bending is checked against axial strength, not fm,d.
 sx='MAX(ABS(S73),ABS(S74),ABS(S75))*O37';sm='MAX(ABS(S76),ABS(S77),ABS(S78))*O37'
 ft='INDEX(Value!$D$5:$D$20,Value!$M$6)*O35/O34'
 edge['C46']=f'=IFERROR(IF(R28=1,H38/H41+C38/C41,MAX((C38+{sx})/C41+({sm})/H41,MAX(0,({sx})-C38)/({ft})+({sm})/H41)),"NZ")'
 # Kser for SLS, Ku=2/3 Kser for ULS (2.2.2(2), equation 2.1; Annex B.2). Identical layers only.
 gs='(1/(1+PI()^2*S40*S36*H27/(S61*(D25*1000)^2)))'
 eisl=f'IF(R28=1,S40*S31,IF(R28=2,2*S40*S31+{gs}/(1+{gs})*S40*S36*E30^2,3*S40*S31+2*{gs}*S40*S36*E30^2))'
 edge['C50']=f'=IFERROR(5*ABS(S33)*(D25*1000)^4/(384*({eisl}))+1.2*ABS(S33)*(D25*1000)^2/(8*S35*S42),"NZ")'
 edge['S81']='=MAX(ABS(S62*S40*S36*S66),ABS(S64*S40*S37*S67))*H27*ABS(S80*O37)/S71'
 edge['A34']='PL NA.1: short-term wind action; confirm external and internal wind coefficients.'
 edge['A35']='NZ = unverified combination / model / fasteners; see documentation.'
 edge['A55']='Deflection limit is a project assumption, not a verified PL limit for studs.'
 edge['A57']='PN-EN 1995-1-1:2010 Annex B; fastener resistance must be verified separately.'
 edge['B43']='kc,min'
 return flat,edge,value


def adapt(source,output):
 maps=formulas();changed=[]
 with ZipFile(source) as src,ZipFile(output,'w',ZIP_DEFLATED) as out:
  for item in src.infolist():
   payload=src.read(item.filename)
   if item.filename in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml','xl/worksheets/sheet3.xml']:
    n=int(item.filename.split('sheet')[-1].split('.')[0])-1;xml=payload.decode('utf-8')
    for address,val in maps[n].items():xml=replace_cell(xml,address,val)
    payload=xml.encode('utf-8');changed.append(item.filename)
   elif item.filename=='xl/workbook.xml':
    xml=payload.decode('utf-8')
    names=''.join(f'<definedName name="{name}">{number}</definedName>' for name,number in PARAMS.items())
    xml=xml.replace('</definedNames>',names+'</definedNames>')
    xml=re.sub(r'<calcPr\b[^>]*/>','<calcPr calcId="0" calcMode="auto" fullCalcOnLoad="1" forceFullCalc="1"/>',xml)
    payload=xml.encode('utf-8');changed.append(item.filename)
   out.writestr(item,payload)
 clean_calc_chain(output,output)
 return changed

if __name__=='__main__':
 output=Path(sys.argv[2]);output.parent.mkdir(parents=True,exist_ok=True)
 print(adapt(sys.argv[1],output))
