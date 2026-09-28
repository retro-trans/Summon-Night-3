import json,hashlib,sys
from pathlib import Path
import chapter_patch_014 as c
from chapter_source_014 import load,ROOT
from dialogue_encoding import control_tokens,encode_dialogue
folder=ROOT/'work/translation/en/chapters_0.1.14/0134'
resource,rows,data=load(134);paths=[p for p in sorted(folder.glob('slice_*.targets.json')) if int(p.name[6:10])>=960]
translated={};inputs={};examined=set()
for p in paths:
 d=json.loads(p.read_text());inputs[str(p.relative_to(ROOT)).replace('\\','/')]=hashlib.sha256(p.read_bytes()).hexdigest()
 for a,b in d['rows_examined']['physical_ranges_inclusive']:examined.update(range(a,b+1))
 for ident,t in d['translations'].items():
  n=t['resource_row']+1808;r=rows[n]
  assert ident==r['id']
  for key in ('source_sha256','source_offset','source_byte_length','reference_instructions'):assert t[key]==r[key]
  src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');assert control_tokens(t['text'])==control_tokens(src);encode_dialogue(t['text'],src)
  translated[n]={**t,'resource_row':n,'text':c.normalize(t['text'])}
assert sorted(translated)==list(range(2768,4392))
c.targets=lambda *a,**k:(translated,inputs)
_,report,_,checks=c.prepare(134,False,True)
summary={'version':'0.1.14','resource_id':'00:00134','assigned_relative_range':[960,2583],'rows_authored':1624,'slice_count':21,'unique_source_rows_examined':len(examined),'examined_physical_range':[min(examined),max(examined)],'review_status':'translator_self_review_only','independent_semantic_review':False,'method':'Direct source translation with neighboring context in consecutive 80-row slices; final slice 24 rows. Author checked meaning while drafting. No independent full-pass review claimed. Earlier 0-239 and 480-959 rows independently reviewed in separate hash-bound reports.','validation':checks,'draft_inputs_sha256':inputs,'remaining_uncertainties':['Gathering Spring and Bawnas remain provisional spellings/translations; see glossary.','Lendora corresponds contextually to Japanese Tridora; English wiki city name takes precedence.','Relative 1866-1869: Kyuuma allows stopping an unreasonable outcome by force; omitted referent kept broad.','Marurur descriptive nicknames retained based on source and character context.','No emulator/UI visual check performed.']}
print(json.dumps({k:v for k,v in summary.items() if k not in ('draft_inputs_sha256','validation')},indent=2));print(json.dumps(checks,indent=2))
if '--write' in sys.argv:(folder/'translator_self_review_0960_2583.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
