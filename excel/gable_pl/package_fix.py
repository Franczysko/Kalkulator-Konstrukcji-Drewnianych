"""Discard optional, stale calculation-chain metadata after formula edits."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re


def clean_calc_chain(source, destination):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + '.tmp')
    with ZipFile(source) as src, ZipFile(temporary, 'w', ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            if entry.filename == 'xl/calcChain.xml':
                continue
            payload = src.read(entry.filename)
            if entry.filename == 'xl/_rels/workbook.xml.rels':
                text = payload.decode('utf-8')
                text = re.sub(r'<Relationship\b(?=[^>]*\bType="[^"]*/calcChain")[^>]*/>', '', text)
                payload = text.encode('utf-8')
            elif entry.filename == '[Content_Types].xml':
                text = payload.decode('utf-8')
                text = re.sub(r'<Override\b(?=[^>]*\bPartName="/xl/calcChain.xml")[^>]*/>', '', text)
                payload = text.encode('utf-8')
            dst.writestr(entry, payload)
    temporary.replace(destination)
