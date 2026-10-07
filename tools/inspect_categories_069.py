"""Read-only inventory of summon spell and item UI pointers in local 068."""
import json,struct,unicodedata,re,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from menu_hotfix_017 import lines_at
BASE=ROOT/'work/output/0.1.68'
def collect():
 rows=[];idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 with GameSource(BASE/'Summon_Night_3_EN_0.1.68.iso') as s:
  st=s.resource('02.DAT',3);ix=parse_index(st,len(st))
  for t in idx['tables']:
   n=t['resource_path'][-1]
   if n not in (13,19):continue
   b=child(st,ix,n);seen={}
   for rec in range(t['record_count']):
    for slot in t['pointer_slots']:
     f=4+rec*t['record_stride']+slot*4;p=struct.unpack_from('<I',b,f)[0]
     if not p:continue
     raw=lines_at(b,p)[0]
     if (n==13 and slot==8) or (n==19 and slot==0):raw=raw[:1]
     texts=[unicodedata.normalize('NFKC',x.decode('cp932')) for x in raw]
     if not any(re.search(r'[\u3040-\u30ff\u3400-\u9fff]',x) for x in texts):continue
     key=(p,slot)
     if key not in seen:seen[key]=dict(table=n,slot=slot,source_offset=p,source_sha256=hashlib.sha256(b'\0\0'.join(raw)).hexdigest(),lines=texts,records=[],pointer_fields=[])
     seen[key]['records'].append(rec);seen[key]['pointer_fields'].append(f)
   rows.extend(seen.values())
 return rows
if __name__=='__main__':
 rows=collect()
 for r in rows:
  if r['table']==13 or any(any(z in x for z in ('サモナイト','ニボシ','素材','イラスト')) for x in r['lines']):print(json.dumps(r,ensure_ascii=False))
 (ROOT/'work/scratch/categories069-current.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 b=(BASE/'EBOOT.elf').read_bytes()
 for text in ['作成する組み合わせを選択してください','作成一覧','送還しますか？','以下のものを手に入れました','はい','いいえ']:
  needle=text.encode('cp932');at=0
  while True:
   at=b.find(needle,at,0x240000)
   if at<0:break
   print('ELF',text,hex(at-192));at+=len(needle)
