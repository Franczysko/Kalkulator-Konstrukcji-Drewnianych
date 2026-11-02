"""QA-only LibreOffice recalculation; delivered Excel does not require this helper.
LO_BIN may select a portable soffice. Pass source.xlsx destination.xlsx .
"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import shutil


def recalculate(source, destination):
    source=Path(source).resolve();destination=Path(destination).resolve()
    with tempfile.TemporaryDirectory(prefix='timber-calc-') as tmp:
        root=Path(tmp);profile=root/'profile';(profile/'user').mkdir(parents=True)
        (profile/'user/registrymodifications.xcu').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"><item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item></oor:items>''')
        out=root/'out';out.mkdir()
        cmd=[os.environ.get('LO_BIN','libreoffice'),'-env:UserInstallation='+profile.as_uri(),'--headless','--convert-to','xlsx:Calc MS Excel 2007 XML','--outdir',str(out),str(source)]
        subprocess.run(cmd,check=True,timeout=180)
        result=out/source.name
        if not result.exists():raise RuntimeError('LibreOffice did not produce recalculated workbook')
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(result,destination)


if __name__=='__main__':recalculate(*sys.argv[1:])
