"""Read only current UI categories and source-bound pointer fields."""
import json,struct,unicodedata,re,argparse
from sn3_archive import ROOT,GameSource,parse_index,child
from menu_hotfix_017 import lines_at
BASE=ROOT/'work/output/0.1.67'
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')
def collect():
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());result=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.67.iso') as src:
  st=src.resource('02.DAT',3);ix=parse_index(st,len(st))
  for t in idx['tables']:
   n=t['resource_path'][-1];data=child(st,ix,n);seen={}
   for row in range(t['record_count']):
    for slot in t['pointer_slots']:
     field=4+row*t['record_stride']+slot*4;p=struct.unpack_from('<I',data,field)[0]
     if not p:continue
     raw=lines_at(data,p)[0]
     if (n==12 and slot in (9,10,11)) or (n in (25,28,31,34) and slot==8) or (n==13 and slot==8):raw=raw[:1]
     texts=[unicodedata.normalize('NFKC',b.decode('cp932')) for b in raw]
     if not any(JP.search(s) for s in texts):continue
     key=(p,slot)
     if key not in seen:seen[key]=dict(table=n,slot=slot,offset=p,category=t['strings'][0]['category'],lines=texts,records=[])
     seen[key]['records'].append(row)
   result.extend(seen.values())
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--table',type=int,nargs='*');p.add_argument('--write',action='store_true');a=p.parse_args();rows=collect()
 print(json.dumps(dict(remaining_by_table={str(n):sum(x['table']==n for x in rows) for n in sorted({x['table'] for x in rows})}),indent=2))
 for r in rows:
  if a.table and r['table'] in a.table:print(json.dumps(r,ensure_ascii=False))
 if a.write:
  out=ROOT/'work/scratch/categories068-current.json';assert not out.exists();out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
