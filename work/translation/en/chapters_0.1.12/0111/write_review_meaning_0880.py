import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_meaning_0880.json';TARGET=BASE/'slice_0880.targets.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(111);d=json.loads(TARGET.read_text(encoding='utf-8'));seen={}
 for i,t in d['translations'].items():
  n=t['resource_row']
  if 880<=n<=959:
   x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert i==x['id'] and t['source_sha256']==x['source_sha256'];encode_dialogue(t['text'],s);seen[n]=i
 assert set(seen)==set(range(880,960))
 return {'resource_id':r['id'],'assigned_range':[880,959],'semantic_complete':True,'rows_examined':{'ranges_inclusive':[[860,979]],'count':120},'reviewed_slices':[{'path':TARGET.name,'sha256':sha(TARGET.read_bytes()),'assigned_range':[880,959]}],'reviewed_source_ids':[seen[n] for n in range(880,960)],'meaning_corrections':[],'uncertainties':[{'resource_row':930,'note':'The source uses the honorific さん; existing “-sir” conveys the requested informal-address point but may be localized further during final editorial review.'},{'resource_row':958,'note':'The fragment intentionally begins the failed pronunciation of Kyle across the slice boundary.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':len(d['reviewed_source_ids'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
