"""Build explicitly numbered Chapter 6 draft slices. Defaults to dry-run."""
import argparse,json
from pathlib import Path
from chapter_source_014 import load,ROOT
from dialogue_encoding import control_tokens

def main():
 p=argparse.ArgumentParser();p.add_argument('draft');p.add_argument('--examined',type=int,nargs=2,required=True);p.add_argument('--write',action='store_true');a=p.parse_args()
 lines=Path(a.draft).read_text(encoding='utf-8').splitlines();targets={}
 for line in lines:
  if not line.strip():continue
  n,t=line.split('|',1);assert int(n) not in targets;targets[int(n)]=t
 r,rows,d=load(180);out=ROOT/'work/translation/en/chapters_0.1.14/0180'
 for start in range(min(targets),max(targets)+1,80):
  end=min(start+79,max(targets));assert start%80==0
  trans={}
  for n in range(start,end+1):
   z=rows[3957+n];original=d[z['source_offset']:z['source_offset']+z['source_byte_length']].decode('cp932');t=targets[n]
   assert control_tokens(t)==control_tokens(original),(n,control_tokens(t),control_tokens(original))
   trans[z['id']]={k:z[k] for k in ('id','source_sha256','source_offset','source_byte_length','reference_instructions')}
   trans[z['id']].update(resource_row=n,physical_ordered_index=3957+n,text=t,status='draft',notes='Self-checked for source alignment and adjacent context; pending independent meaning review.')
  result={'resource_id':r['id'],'section':'main-tail','assigned_range':[start,end],'physical_ordered_index_range':[3957+start,3957+end],'rows_examined':{'ranges_inclusive':[[3957+a.examined[0],3957+a.examined[1]]],'count':a.examined[1]-a.examined[0]+1},'uncertainties':['Unlisted fantasy food and species terms use provisional transliterations; glossary review requested.'],'translations':trans}
  print(json.dumps({'mode':'write' if a.write else 'dry-run','range':[start,end],'rows':len(trans),'samples':[(n,targets[n]) for n in (start,start+1,end)]},ensure_ascii=False))
  if a.write:(out/f'slice_{start:04d}.targets.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
