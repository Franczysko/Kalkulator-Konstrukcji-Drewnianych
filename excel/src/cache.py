"""Copy evaluated formula caches into original XLSX without altering original formulas/charts."""
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET
from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries, coordinate_to_tuple

NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
ET.register_namespace('',NS)


def inject(original,calculated,output):
    data=load_workbook(calculated,data_only=True)
    with ZipFile(original) as src, ZipFile(output,'w',ZIP_DEFLATED) as dst:
        for info in src.infolist():
            payload=src.read(info.filename)
            if info.filename.startswith('xl/worksheets/sheet') and info.filename.endswith('.xml'):
                number=int(Path(info.filename).stem[5:])-1;sheet=data.worksheets[number]
                root=ET.fromstring(payload)
                arrays=[range_boundaries(f.get('ref')) for f in root.findall('.//{%s}f'%NS) if f.get('t')=='array']
                for c in root.findall('.//{%s}c'%NS):
                    coord=c.get('r');r,col=coordinate_to_tuple(coord)
                    is_array=any(a<=col<=cc and b<=r<=d for a,b,cc,d in arrays)
                    if c.find('{%s}f'%NS) is None and not is_array:continue
                    value=sheet[coord].value
                    if sheet[coord].data_type=='e':raise ValueError((sheet.title,coord,value))
                    v=c.find('{%s}v'%NS)
                    if v is None:v=ET.SubElement(c,'{%s}v'%NS)
                    if isinstance(value,str):c.set('t','str');v.text=value
                    elif isinstance(value,bool):c.set('t','b');v.text=str(int(value))
                    elif value is None:c.set('t','str');v.text=''
                    else:c.attrib.pop('t',None);v.text=str(value)
                payload=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            if info.filename.startswith('xl/charts/chart') and info.filename.endswith('.xml'):
                chartns='http://schemas.openxmlformats.org/drawingml/2006/chart'
                root=ET.fromstring(payload)
                for nr in root.findall('.//{%s}numRef'%chartns):
                    formula=nr.find('{%s}f'%chartns).text
                    sheetname,span=formula.rsplit('!',1)
                    sheetname=sheetname.strip("'").replace("''", "'")
                    a,b,cc,d=range_boundaries(span)
                    values=[data[sheetname].cell(r,c).value for r in range(b,d+1) for c in range(a,cc+1)]
                    cache=nr.find('{%s}numCache'%chartns)
                    if cache is not None:nr.remove(cache)
                    cache=ET.SubElement(nr,'{%s}numCache'%chartns)
                    ET.SubElement(cache,'{%s}formatCode'%chartns).text='General'
                    ET.SubElement(cache,'{%s}ptCount'%chartns,{'val':str(len(values))})
                    for i,value in enumerate(values):
                        if isinstance(value,(int,float)):
                            pt=ET.SubElement(cache,'{%s}pt'%chartns,{'idx':str(i)})
                            ET.SubElement(pt,'{%s}v'%chartns).text=str(value)
                payload=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            dst.writestr(info,payload)


if __name__=='__main__':inject(*sys.argv[1:])
