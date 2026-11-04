"""Regression of the exact stale-calcChain repair reported by Microsoft Excel."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json,posixpath,subprocess,tempfile
from package_fix import clean_calc_chain

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def stale_records(path):
 with ZipFile(path) as z:
  root=etree.fromstring(z.read('xl/workbook.xml'))
  rels=etree.fromstring(z.read('xl/_rels/workbook.xml.rels'))
  targets={r.get('Id'):'xl/'+r.get('Target') for r in rels if r.get('Type').endswith('/worksheet')}
  sheets={s.get('sheetId'):etree.fromstring(z.read(targets[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')])) for s in root.findall('m:sheets/m:sheet',NS)}
  bad=[];sid=None
  for item in etree.fromstring(z.read('xl/calcChain.xml')):
   sid=item.get('i',sid);addr=item.get('r');cells=sheets[sid].xpath('.//m:c[@r=$address]',namespaces=NS,address=addr)
   if not cells or cells[0].find('m:f',NS) is None:bad.append({'sheet_id':sid,'cell':addr})
  return bad


def validate_package(path):
 with ZipFile(path) as z:
  assert z.testzip() is None
  assert 'xl/calcChain.xml' not in z.namelist()
  assert b'/calcChain' not in z.read('xl/_rels/workbook.xml.rels')
  assert b'/xl/calcChain.xml' not in z.read('[Content_Types].xml')
  for name in z.namelist():
   if name.endswith('.rels'):
    base='' if name=='_rels/.rels' else name.rsplit('/_rels/',1)[0]
    for r in etree.fromstring(z.read(name)):
     if r.get('TargetMode')=='External':continue
     target=r.get('Target').split('#',1)[0]
     if not target:continue
     resolved=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(base,target))
     assert resolved in z.namelist(),(name,resolved)


def run():
 project=Path(__file__).resolve().parents[2]
 with tempfile.TemporaryDirectory(prefix='calc-chain-regression-') as tmp:
  before=Path(tmp)/'reported.xlsx';after=Path(tmp)/'clean.xlsx';again=Path(tmp)/'again.xlsx'
  before.write_bytes(subprocess.check_output(['git','show','9e2d61c:excel/output/Gable_panel_stud_PL.xlsx'],cwd=project))
  stale=stale_records(before);assert {(r['sheet_id'],r['cell']) for r in stale}=={('6','P60'),('1','P60')}
  clean_calc_chain(before,after);validate_package(after)
  with ZipFile(before) as a,ZipFile(after) as b:
   changed={n for n in b.namelist() if a.read(n)!=b.read(n)}
   assert changed=={'[Content_Types].xml','xl/_rels/workbook.xml.rels'}
   assert set(a.namelist())-set(b.namelist())=={'xl/calcChain.xml'}
  clean_calc_chain(after,again)
  with ZipFile(after) as a,ZipFile(again) as b:
   assert a.namelist()==b.namelist() and all(a.read(n)==b.read(n) for n in a.namelist())
 validate_package(project/'excel/output/Gable_panel_stud_PL.xlsx')
 report={'reported_stale_records':stale,'repair_changes_only_metadata':True,'all_formulas_values_styles_graphics_preserved':True,'package_relationship_targets_exist':True,'cleanup_idempotent':True,'actual_microsoft_excel_open_test':'not available in this Linux environment'}
 Path(__file__).with_name('repair_test_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('Stale P60 records reproduced; package cleanup, relationships and idempotence passed')

if __name__=='__main__':run()
