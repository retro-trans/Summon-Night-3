"""Author's Chapter 4 slice drafts; validate and preview before --write."""
import sys,json,argparse
from pathlib import Path
from chapter_source_014 import load,ROOT
from dialogue_encoding import control_tokens,encode_dialogue

def main():
 p=argparse.ArgumentParser();p.add_argument('draft');p.add_argument('--write',action='store_true');a=p.parse_args()
 d=json.loads(Path(a.draft).read_text(encoding='utf-8'));resource,allrows,data=load(134);rows=allrows[1808:]
 start=d['start'];lines=d['text'].splitlines();assert len(lines)==min(80,len(rows)-start),(start,len(lines))
 trans={}
 for n,text in enumerate(lines,start):
  r=rows[n];original=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
  assert control_tokens(text)==control_tokens(original),(n,'controls',control_tokens(original),text)
  encode_dialogue(text,original)
  trans[r['id']]={**r,'resource_row':n,'text':text,'status':'draft','notes':'Human-language model authored from source and adjacent context; no independent semantic review.'}
 doc={'resource_id':resource['id'],'assigned_range':[start,start+len(lines)-1], 'rows_examined':{'physical_ranges_inclusive':d['examined'],'count':sum(y-x+1 for x,y in d['examined'])},'review_status':'author_self_check_only','uncertainties':d.get('uncertainties',[]),'translations':trans}
 print(json.dumps({'mode':'write' if a.write else 'dry-run','range':doc['assigned_range'],'count':len(lines),'first':lines[:3],'last':lines[-3:]},ensure_ascii=False))
 if a.write:
  dest=ROOT/'work/translation/en/chapters_0.1.14/0134'/f'slice_{start:04d}.targets.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()

