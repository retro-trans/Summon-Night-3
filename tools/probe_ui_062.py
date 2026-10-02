"""Read-only inspection of the latest reported UI strings and consumers."""
import struct,unicodedata,json
from sn3_archive import ROOT,GameSource,parse_index,child
from spell_name_059 import label
from probe_report_061 import dump
BASE=ROOT/'work/output/0.1.61'
def main():
 with GameSource(BASE/'Summon_Night_3_EN_0.1.61.iso') as s:
  st=s.resource('02.DAT',3);ix=parse_index(st,len(st))
  for n,stride,slots in [(12,88,[9,10,11,12]),(13,40,[8]),(25,48,[8,9,10])]:
   b=child(st,ix,n);count=struct.unpack_from('<I',b)[0]
   # The summon table's stride is defined in the source index.
   source=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());t=next(t for t in source['tables'] if t['resource_path']==[3,n]);stride=t['record_stride'];slots=t['pointer_slots']
   print('table',n,count,stride,slots)
   for rec in range(count):
    fields={slot:label(b,4+rec*stride+slot*4) for slot in slots}
    if (n==12 and rec in (20,21,22)) or any(any(z in text for z in ['抜剣覚醒','踊り好き','すすオトシ','すすシバキ','闇シバキ']) for text in fields.values()):print(rec,json.dumps(fields,ensure_ascii=False))
  index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
  for t in index['tables']:
   if len(t['resource_path'])!=2 or t['resource_path'][0]!=3:continue
   n=t['resource_path'][1];b=child(st,ix,n);stride=t['record_stride']
   for rec in range(t['record_count']):
    for slot in t['pointer_slots']:
     text=label(b,4+rec*stride+slot*4)
     if any(z in text for z in ['抜剣','剣の力を解放','全異常・憑依']):print('awakening',n,rec,slot,json.dumps(text,ensure_ascii=False))
  b=child(st,ix,12);p=struct.unpack_from('<I',b,4+23*52+48)[0]
  end=b.find(b'\0\0\0\0',p)
  print('Mujina description raw',b[p:end+4].decode('cp932').replace('\0',' | '))
 elf=(BASE/'EBOOT.elf').read_bytes()
 print('summon labels/binds');dump(elf,0x1545f0,0x154720)
 for va in range(0x154950,0x154d00,4):
  w=struct.unpack_from('<I',elf,va+192)[0]
  if w>>26==3 and (w&0x3ffffff)<<2 in (0x1cbdec,0x347b5c):dump(elf,va-24,va+12)
if __name__=='__main__':main()
