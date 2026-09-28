"""Independent source-bound review ledger for Chapter 2 rows 560-1119."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_0560_1119.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(88); files=[BASE/f'slice_{n:04d}.targets.json' for n in range(560,1120,80)]; docs=[json.loads(p.read_text(encoding='utf-8')) for p in files];seen={}
 for p,d in zip(files,docs):
  for ident,t in d['translations'].items():
   n=t['resource_row']
   if 560<=n<=1119:
    x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert ident==x['id'] and t['source_sha256']==x['source_sha256'] and t['text'];encode_dialogue(t['text'],s);assert n not in seen;seen[n]=ident
 assert set(seen)==set(range(560,1120))
 return {'resource_id':r['id'],'reviewed_range':[560,1119],'rows_examined':{'ranges_inclusive':[[540,1139]],'count':600},'reviewed_row_count':560,'target_files_sha256':{p.name:sha(p.read_bytes()) for p in files},'reviewed_source_ids':[seen[n] for n in range(560,1120)],'corrections':[],'uncertainties':[{'scope':'meaning review','note':'No replacement required after independent source/context pass; source identity, runtime controls, and nonempty fragment continuity were revalidated.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':d['reviewed_row_count'],'files':list(d['target_files_sha256'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
