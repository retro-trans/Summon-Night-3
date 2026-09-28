"""Hash and structurally verify the author's completed draft scopes; no independent review claim."""
import argparse,hashlib,json
from pathlib import Path
from chapter_source_014 import ROOT,load
from dialogue_encoding import control_tokens,encode_dialogue

def check(folder,start,end,shift,examined,filename,uncertainties):
 resource,rows,data=load(180);byrow={};hashes={};paths=[]
 for p in sorted(folder.glob('slice_*.targets.json')):
  doc=json.loads(p.read_text(encoding='utf-8'))
  if doc['assigned_range'][1]<start or doc['assigned_range'][0]>end:continue
  assert start<=doc['assigned_range'][0]<=doc['assigned_range'][1]<=end
  hashes[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest();paths.append(p)
  for identity,t in doc['translations'].items():
   n=t['resource_row'];assert n not in byrow;z=rows[n+shift]
   assert identity==z['id']==t['id']
   for k in ('source_sha256','source_offset','source_byte_length','reference_instructions'):assert t[k]==z[k],(n,k)
   assert t['physical_ordered_index']==n+shift
   original=data[z['source_offset']:z['source_offset']+z['source_byte_length']].decode('cp932')
   assert control_tokens(original)==control_tokens(t['text']);encode_dialogue(t['text'],original)
   byrow[n]=t
 assert sorted(byrow)==list(range(start,end+1))
 doc={'schema_version':1,'version':'0.1.14','resource_id':resource['id'],'review_type':'translator_self_review','independent_review':False,'status':'author_source_alignment_and_meaning_self_check_complete','assigned_range':[start,end],'physical_ordered_index_range':[start+shift,end+shift],'rows_in_scope':len(byrow),'rows_examined':{'ranges_inclusive':[examined],'count':examined[1]-examined[0]+1},'reviewed_rows':sorted(byrow),'reviewed_source_ids':[byrow[n]['id'] for n in sorted(byrow)],'draft_inputs_sha256':hashes,'checks':{'exact_source_anchor_metadata':'pass','coverage':'pass','control_token_order':'pass','two_byte_cp932_encoding':'pass','independent_meaning_review':'not claimed','in_game_visual_validation':'pending'},'uncertainties':uncertainties,'meaning_corrections':[],'notes':['Every assigned source row was read directly with adjacent scene context; Japanese was not saved in draft transcripts.','English was drafted in full without a source byte budget.','Native fixed-line notifications were redistributed across their existing lines, preserving their combined meaning.']}
 return folder/filename,doc

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();base=ROOT/'work/translation/en/chapters_0.1.14'
 common=['Rigd, Rushana, Canel and Gathering Spring are provisional terminology; sources and status are recorded in work/glossary/common_terms_0.1.14.json.','Fountain of Youth Japanese-English mapping is a contextual inference from the external references supplied by the coordinating agent.','Meimei incantations use literal interpretive English, not established localized spell text.','Row3145 is an isolated sentence-ending particle in the source; rendered as Right? without inventing another sentence.','Rows3731-3734 preserve both Shartos and the literal descriptive epithet Azure Sage Emperor because the source explicitly introduces the written title and pronunciation together. This epithet is not an official localization claim. Generic sword references use Shartos.','Feature names and the minigame labels may require reconciliation with final UI terminology.']
 mainnotes=json.loads((ROOT/'docs/chapter6_draft_selfcheck_0.1.14.json').read_text(encoding='utf-8'))['uncertainties']
 for folder,start,end,shift,examined,name,notes in [(base/'common_0180',0,3956,0,[0,3966],'translator_self_review.json',common),(base/'0180',160,1871,3957,[4107,5828],'translator_self_review_0160_1871.json',mainnotes)]:
  out,d=check(folder,start,end,shift,examined,name,notes)
  print(json.dumps({'mode':'write' if a.write else 'dry-run','output':out.relative_to(ROOT).as_posix(),'rows':d['rows_in_scope'],'files':len(d['draft_inputs_sha256']),'independent_review':False,'sample_hashes':list(d['draft_inputs_sha256'].items())[:2]},ensure_ascii=False))
  if a.write:out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
