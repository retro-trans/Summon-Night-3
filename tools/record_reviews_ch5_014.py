"""Write bounded source-checked review records. Dry-run default."""
import argparse,json,hashlib
from chapter_source_014 import load
from dialogue_encoding import control_tokens,encode_dialogue
from sn3_archive import ROOT
FIXES={29:'We have not had',30:'our lesson yet...',68:'to gain admission to the military',69:'academy, no matter what.',72:'to help me achieve that.',73:'That duty should',74:'take priority over',75:"everything else, shouldn't it?",76:'Am I wrong!?',101:'me.',290:'with you, right?',302:'with you, right?',314:'with you, right?',327:'with you, right?',376:'hereby asks...',379:'hereby asks...',382:'hereby asks...',385:'hereby asks...',386:"I'm counting on you, okay?"}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r,rows,d=load(157);folder=ROOT/'work/translation/en/chapters_0.1.14/0157';allpaths=sorted(folder.glob('slice_*.targets.json'))
 for low,high,kind,name in [(0,479,'independent_meaning_review','independent_review.json'),(480,2704,'translator_self_review','translator_self_review.json')]:
  paths=[p for p in allpaths if low<=json.loads(p.read_text(encoding='utf-8'))['assigned_range'][0]<=high];slices=[];seen=[]
  for path in paths:
   doc=json.loads(path.read_text(encoding='utf-8'));rr=sorted(v['resource_row'] for v in doc['translations'].values());seen+=rr
   slices.append({'target_file':str(path.relative_to(ROOT)).replace('\\','/'),'target_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'assigned_range':[min(rr),max(rr)],'translation_count':len(rr)})
  assert seen==list(range(low,high+1))
  fixes=[]
  for n,t in FIXES.items():
   if not low<=n<=high:continue
   row=rows[n+1808];src=d[row['source_offset']:row['source_offset']+row['source_byte_length']].decode('cp932');encode_dialogue(t,src);fixes.append({'resource_row':n,'source_sha256':row['source_sha256'],'text':t})
  doc={'resource_id':'00:00157','review_type':kind,'semantic_complete':True,'independent_review':kind=='independent_meaning_review','reviewed_rows':seen,'reviewed_slices':slices,'corrections':fixes,'rows_examined':{'relative_range_inclusive':[0,484] if low==0 else [472,2704],'count':485 if low==0 else 2233},'method':'Compared all source and target rows in six 80-row slices with adjacent context.' if low==0 else 'Author source-context self-check during drafting, followed by targeted repairs and exact-control validation; not an independent second pass.','uncertainties':['Companion gender was not established by this source scene; neutral question tags replace unsupported he/she.' ,'The initial three student branches explicitly refer to unfinished lessons; the final branch only says the lesson has not happened yet and is retained without assuming it started.'] if low==0 else ['Takeshi uses the root-verified SN6 gallery spelling, provisionally mapped to the SN3 thunder spirit.','Genji and the male/female protagonist variants are kept neutral where the source narration omits identity.'],'change_log':['Build 0.1.14: completed bounded Chapter 5 meaning review.']}
  print(name,'rows',len(seen),'slices',len(slices),'corrections',fixes)
  if a.write:(folder/name).write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
