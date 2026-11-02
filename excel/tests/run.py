"""Reproducible QA pipeline. Requires LibreOffice (LO_BIN override supported)."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recalculate import recalculate
from cache import inject


def run():
    subprocess.run([sys.executable,str(ROOT/'src/generate.py')],check=True)
    source=ROOT/'output/Kalkulator_konstrukcji_drewnianych.xlsx'
    with tempfile.TemporaryDirectory(prefix='timber-tests-') as tmp:
        root=Path(tmp);baseline=root/'baseline.xlsx'
        recalculate(source,baseline)
        subprocess.run([sys.executable,str(ROOT/'tests/validate.py'),str(baseline),'baseline'],check=True)
        subprocess.run([sys.executable,str(ROOT/'tests/make_variants.py')],check=True)
        for name in ['triangle','changed_geometry','overload','missing','mechanism']:
            dest=root/(name+'.xlsx')
            recalculate(Path('/tmp/timber-variants')/(name+'.xlsx'),dest)
            subprocess.run([sys.executable,str(ROOT/'tests/validate.py'),str(dest),name],check=True)
        cached=root/'cached.xlsx';inject(source,baseline,cached)
        source.write_bytes(cached.read_bytes())
        # Verify serialization/reopening and original cached values, including formula arrays.
        subprocess.run([sys.executable,str(ROOT/'tests/validate.py'),str(source),'delivered'],check=True)
    results=[]
    for p in sorted((ROOT/'tests').glob('*-results.json')):
        if p.stem.startswith('Kalkulator_'):continue
        r=json.loads(p.read_text());results.append({'run':p.name,'passed':r['passed'],'failed':r['failed']})
    (ROOT/'tests/summary.json').write_text(json.dumps({'runs':results,'note':'Counts are numeric assertions, not independent structural design examples.'},ensure_ascii=False,indent=2))
    print('QA complete; delivered XLSX contains verified cached values.')


if __name__=='__main__':run()
