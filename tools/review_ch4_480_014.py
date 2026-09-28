"""Independent Chapter 4 meaning corrections for 480--959; dry-run default."""
import json,hashlib,sys
from chapter_source_014 import load,ROOT
from dialogue_encoding import encode_dialogue
folder=ROOT/'work/translation/en/chapters_0.1.14/0134'
r,rows,data=load(134);rows=rows[1808:]
review={'resource_id':r['id'],'review_type':'independent_meaning_review','semantic_complete':True,'reviewed_slices':[],'corrections':[],'uncertainties':[{'resource_rows':[532,533],'note':'Lendora sword style follows the English wiki city name; correspondence with Japanese Tridora is contextual, not a direct bilingual attestation.'}],'method':'Reviewer independently read original source and existing MT for every row, including eight neighboring rows on either side; drafted meaning corrections without MT services. Names use user-selected SN6 gallery. Final literal names/sounds preserved where appropriate.'}
for start in range(480,960,80):
 p=folder/f'slice_{start:04d}.targets.json';original=json.loads(p.read_text(encoding='utf-8'));draft=json.loads((folder/f'review_draft_{start:04d}.json').read_text(encoding='utf-8'));lines=draft['text'].splitlines();assert len(lines)==80,(start,len(lines))
 review['reviewed_slices'].append({'target_file':str(p.relative_to(ROOT)).replace('\\','/'),'target_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'assigned_range':[start,start+79],'translation_count':80,'rows_examined':{'ranges_inclusive':[[472,967]],'count':496}})
 for n,text in enumerate(lines,start):
  row=rows[n];src=data[row['source_offset']:row['source_offset']+row['source_byte_length']].decode('cp932');encode_dialogue(text,src)
  if text!=original['translations'][row['id']]['text']:review['corrections'].append({'resource_row':n,'id':row['id'],'source_sha256':row['source_sha256'],'text':text})
print(json.dumps({'mode':'write' if '--write' in sys.argv else 'dry-run','reviewed_rows':480,'unique_source_rows_examined':496,'correction_count':len(review['corrections']),'samples':[x for x in review['corrections'] if x['resource_row'] in (480,487,488,649,658,735,746,813,945,959)]},indent=2))
if '--write' in sys.argv:(folder/'review_meaning_0480_0959.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
