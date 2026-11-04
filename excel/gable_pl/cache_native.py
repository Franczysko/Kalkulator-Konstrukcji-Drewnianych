"""Insert evaluated caches without reserializing original worksheet/layout XML."""
from zipfile import ZipFile,ZIP_DEFLATED
from xml.sax.saxutils import escape
from openpyxl import load_workbook
from datetime import date,datetime
from openpyxl.utils.datetime import to_excel
import re

CELL=re.compile(r'<c\b[^>]*?(?:/>|>.*?</c>)',re.S)


def cache(source,calculated,destination):
 data=load_workbook(calculated,data_only=True)
 with ZipFile(source) as src,ZipFile(destination,'w',ZIP_DEFLATED) as dst:
  for item in src.infolist():
   payload=src.read(item.filename)
   if re.fullmatch(r'xl/worksheets/sheet[123]\.xml',item.filename):
    sheet=data.worksheets[int(item.filename.split('sheet')[-1].split('.')[0])-1]
    def replace(match):
     text=match.group(0)
     if not re.search(r'<f(?:\s|>)',text):return text
     addr=re.search(r'\br="([A-Z]+\d+)"',text).group(1);c=sheet[addr];value=c.value
     if c.data_type=='e':raise ValueError((sheet.title,addr,value))
     if isinstance(value,(date,datetime)):value=to_excel(value,data.epoch)
     opening=text.split('>',1)[0]+'>';body=text[len(opening):]
     opening=re.sub(r'\s+t="[^"]*"','',opening)
     if isinstance(value,str) or value is None:opening=opening[:-1]+' t="str">';v=escape(value or '')
     elif isinstance(value,bool):opening=opening[:-1]+' t="b">';v=str(int(value))
     else:v=str(value)
     body=re.sub(r'<v(?:\s[^>]*)?>.*?</v>','',body,flags=re.S)
     body=body.replace('</c>','<v>'+v+'</v></c>')
     return opening+body
    payload=CELL.sub(replace,payload.decode('utf-8')).encode('utf-8')
   dst.writestr(item,payload)
