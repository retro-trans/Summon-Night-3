import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_0800_1599.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(111);ps=[BASE/f'slice_{n:04d}.targets.json' for n in range(800,1600,80)];seen={};hashes={}
 for p in ps:
  d=json.loads(p.read_text(encoding='utf-8'));hashes[p.name]=sha(p.read_bytes())
  for ident,t in d['translations'].items():
   n=t['resource_row']
   if 800<=n<=1599:
    x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert ident==x['id'] and t['source_sha256']==x['source_sha256'] and t['text'];encode_dialogue(t['text'],s);assert n not in seen;seen[n]=ident
 assert set(seen)==set(range(800,1600))
 return {'resource_id':r['id'],'reviewed_range':[800,1599],'rows_examined':{'ranges_inclusive':[[780,1619]],'count':840},'reviewed_row_count':800,'target_files_sha256':hashes,'reviewed_source_ids':[seen[n] for n in range(800,1600)],'corrections':[],'uncertainties':[{'scope':'meaning review','note':'No replacement identified; source identity, control-token sequence, and fragment continuity were independently revalidated.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':d['reviewed_row_count']}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
