"""Pack human-authored Chapter 5 remaining dialogue; dry-run default."""
import argparse,json
from chapter_source_014 import load
from dialogue_encoding import control_tokens,encode_dialogue
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/translation/en/chapters_0.1.14/0157';resource,rows,data=load(157);entries={}
 for line in (folder/'authored_remainder.txt').read_text(encoding='utf-8').splitlines():
  if not line or line.startswith('#'):continue
  n,t=line.split('|',1);n=int(n);assert n not in entries
  # Glossary name pass follows meaning edits; do not revert Yukres.
  entries[n]=t.replace('Yucress','Yukres')
 for start in range(2288,4513,80):
  end=min(start+80,4513)
  if not all(n in entries for n in range(start,end)):continue
  out={'resource_id':resource['id'],'assigned_range':[start-1808,end-1809],'rows_examined':{'physical_ranges_inclusive':[[max(2280,start-8),min(4512,end+8)]],'count':min(4512,end+8)-max(2280,start-8)+1},'review_status':'author_self_check_only','uncertainties':['Implicit subjects retained as neutral where context does not identify them; no independent review claimed.'],'translations':{}}
  for n in range(start,end):
   r=rows[n];t=entries[n];src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');assert control_tokens(t)==control_tokens(src),(n,t,control_tokens(src));encode_dialogue(t,src)
   out['translations'][r['id']]={**{k:r[k] for k in ('id','source_sha256','source_offset','source_byte_length','reference_instructions')},'resource_row':n-1808,'text':t,'status':'draft','notes':'Authored with adjacent scene context; no byte budget.'}
  dest=folder/f'slice_{start-1808:04d}.targets.json';print(dest.name,len(out['translations']),entries[start],'=>',entries[end-1])
  if a.write:dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Authored rows',len(entries))
if __name__=='__main__':main()
