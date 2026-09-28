import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_meaning_0960.json';TARGET=BASE/'slice_0960.targets.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(111);d=json.loads(TARGET.read_text(encoding='utf-8'));seen={}
 for i,t in d['translations'].items():
  n=t['resource_row']
  if 960<=n<=1039:
   x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert i==x['id'] and t['source_sha256']==x['source_sha256'];encode_dialogue(t['text'],s);seen[n]=i
 assert set(seen)==set(range(960,1040))
 return {'resource_id':r['id'],'assigned_range':[960,1039],'semantic_complete':True,'rows_examined':{'ranges_inclusive':[[940,1059]],'count':120},'reviewed_slices':[{'path':TARGET.name,'sha256':sha(TARGET.read_bytes()),'assigned_range':[960,1039]}],'reviewed_source_ids':[seen[n] for n in range(960,1040)],'meaning_corrections':[],'uncertainties':[{'resource_row':1025,'note':'妖怪 is rendered as monster; retain as a generic creature term unless the island glossary establishes a stricter English realm category.'},{'resource_row':960,'note':'The stammered attempt at Kyle crosses rows 958–961; existing English retains the failed pronunciation without adding a referent.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':len(d['reviewed_source_ids'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
