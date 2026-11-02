"""Optional PDF/PNG QA export. Requires requirements-preview.txt and LibreOffice."""
from pathlib import Path
import os
import subprocess
import tempfile
import fitz
ROOT=Path(__file__).resolve().parents[1]


def export():
    source=ROOT/'output/Kalkulator_konstrukcji_drewnianych.xlsx'
    with tempfile.TemporaryDirectory(prefix='timber-pdf-') as temp:
        root=Path(temp);profile=root/'profile'
        subprocess.run([os.environ.get('LO_BIN','libreoffice'),'-env:UserInstallation='+profile.as_uri(),
                        '--headless','--convert-to','pdf','--outdir',str(root),str(source)],check=True,timeout=180)
        doc=fitz.open(root/(source.stem+'.pdf'));starts={}
        for i,page in enumerate(doc):
            text=page.get_text()
            for title,key in [('ŚCIANA SZKIELETOWA — KARTA DANYCH','wall'),
                              ('WYSUWNICA PREFABRYKOWANA — KARTA DANYCH','ladder'),
                              ('RAPORT OBLICZENIOWY — KONSTRUKCJE DREWNIANE','report'),
                              ('TESTY I WALIDACJA','after_report')]:
                if title in text:starts[key]=i
        for key,name in [('wall','sciana-podglad'),('ladder','wysuwnica-podglad')]:
            doc[starts[key]].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(ROOT/'docs'/(name+'.png'))
        report=fitz.open();report.insert_pdf(doc,from_page=starts['report'],to_page=starts['after_report']-1)
        for i,page in enumerate(report):
            page.add_redact_annot(fitz.Rect(0,page.rect.height-23,page.rect.width,page.rect.height),fill=(1,1,1))
            page.apply_redactions()
            page.insert_text((32,page.rect.height-12),f'Raport przykladowy - NIEZWERYFIKOWANE | {i+1}/{len(report)} | 2026-11-02',fontsize=7)
        report.save(ROOT/'output/Raport_przykladowy_NIEZWERYFIKOWANE.pdf')
        print('PDF pages:',len(report),'and two card previews exported')


if __name__=='__main__':export()
