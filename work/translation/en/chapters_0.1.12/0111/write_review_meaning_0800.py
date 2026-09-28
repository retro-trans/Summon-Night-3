import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_meaning_0800.json';TARGET=BASE/'slice_0800.targets.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(111);d=json.loads(TARGET.read_text(encoding='utf-8'));seen={}
 for ident,t in d['translations'].items():
  n=t['resource_row']
  if 800<=n<=879:
   x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert ident==x['id'] and t['source_sha256']==x['source_sha256'];encode_dialogue(t['text'],s);seen[n]=ident
 assert set(seen)==set(range(800,880))
 return {'resource_id':r['id'],'assigned_range':[800,879],'semantic_complete':True,'rows_examined':{'ranges_inclusive':[[780,899]],'count':120},'reviewed_slices':[{'path':TARGET.name,'sha256':sha(TARGET.read_bytes()),'assigned_range':[800,879]}],'reviewed_source_ids':[seen[n] for n in range(800,880)],'meaning_corrections':[{'resource_row':814,'source_id':seen[814],'replacement_text':'Hee hee♪ See?','reason':'Restores the source musical-note mark.'},{'resource_row':826,'source_id':seen[826],'replacement_text':'Oh, how lovely♪','reason':'Restores the source musical-note mark.'}],'uncertainties':[{'resource_row':875,'note':'Source is a short disgruntled interjection; existing Hmph is an acceptable contextual rendering.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':len(d['reviewed_source_ids']),'corrections':len(d['meaning_corrections'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
