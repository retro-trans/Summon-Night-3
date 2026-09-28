"""Build common Chapter 4-8 draft slices0-3956; dry-run by default."""
import argparse,json
from pathlib import Path
from chapter_source_014 import load,ROOT
from dialogue_encoding import control_tokens,encode_dialogue

def main():
 p=argparse.ArgumentParser();p.add_argument('draft');p.add_argument('--examined',type=int,nargs=2,required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
 targets={}
 for line in Path(a.draft).read_text(encoding='utf-8').splitlines():
  if not line.strip():continue
  n,t=line.split('|',1);assert int(n) not in targets;targets[int(n)]=t
 r,rows,d=load(180);out=ROOT/'work/translation/en/chapters_0.1.14/common_0180'
 assert 0<=min(targets)<=max(targets)<3957
 for start in range(min(targets),max(targets)+1,80):
  end=min(start+79,max(targets));assert start%80==0
  trans={}
  for n in range(start,end+1):
   z=rows[n];original=d[z['source_offset']:z['source_offset']+z['source_byte_length']].decode('cp932');t=targets[n]
   assert control_tokens(t)==control_tokens(original),(n,control_tokens(t),control_tokens(original));encode_dialogue(t,original)
   trans[z['id']]={k:z[k] for k in ('id','source_sha256','source_offset','source_byte_length','reference_instructions')}
   trans[z['id']].update(resource_row=n,physical_ordered_index=n,text=t,status='draft',notes='Self-checked for exact source alignment and adjacent context. No independent review is claimed.')
  result={'resource_id':r['id'],'section':'common-c6-c8','assigned_range':[start,end],'physical_ordered_index_range':[start,end],'rows_examined':{'ranges_inclusive':[a.examined],'count':a.examined[1]-a.examined[0]+1},'uncertainties':['Feature and minigame terminology may require reconciliation with final UI wording.'],'translations':trans}
  print(json.dumps({'mode':'write' if a.write else 'dry-run','range':[start,end],'rows':len(trans),'samples':[(n,targets[n]) for n in (start,start+1,end)]},ensure_ascii=False))
  if a.write:
   out.mkdir(exist_ok=True);(out/f'slice_{start:04d}.targets.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
