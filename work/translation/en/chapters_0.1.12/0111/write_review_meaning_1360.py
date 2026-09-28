import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue
BASE=Path(__file__).parent;OUT=BASE/'review_meaning_1360.json';TARGET=BASE/'slice_1360.targets.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def build():
 r,rows,data=chapter_source(111);d=json.loads(TARGET.read_text(encoding='utf-8'));seen={}
 for i,t in d['translations'].items():
  n=t['resource_row']
  if 1360<=n<=1439:
   x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');assert i==x['id'] and t['source_sha256']==x['source_sha256'];encode_dialogue(t['text'],s);seen[n]=i
 assert set(seen)==set(range(1360,1440))
 corrections=[
  {'resource_row':1389,'source_id':seen[1389],'replacement_text':"Sapureth, Knight of",'reason':'The source identifies Falzen as the Knight of the Underworld from Sapureth; the draft instead makes an ungrammatical "Spirit Realm Underworld" title and omits Sapureth.'},
  {'resource_row':1390,'source_id':seen[1390],'replacement_text':'the Underworld, Falzen...','reason':'Completes the preceding title and retains the speaker-introduced name.'},
 ]
 for correction in corrections:
  n=correction['resource_row'];x=rows[n];s=data[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');encode_dialogue(correction['replacement_text'],s)
 return {'resource_id':r['id'],'assigned_range':[1360,1439],'semantic_complete':True,'rows_examined':{'ranges_inclusive':[[1340,1459]],'count':120},'reviewed_slices':[{'path':TARGET.name,'sha256':sha(TARGET.read_bytes()),'assigned_range':[1360,1439]}],'reviewed_source_ids':[seen[n] for n in range(1360,1440)],'meaning_corrections':corrections,'uncertainties':[{'resource_row':1393,'detail':'四者 (four parties) is rendered "the four"; the source leaves their exact institutional label implicit, so the draft preserves that ambiguity.'}]}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();d=build();print(json.dumps({'mode':'write' if a.write else 'dry-run','reviewed':len(d['reviewed_source_ids'])}));a.write and OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
