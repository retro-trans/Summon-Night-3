import json,sys,hashlib
from pathlib import Path
from chapter_source_014 import load,ROOT
from dialogue_encoding import encode_dialogue,control_tokens
from build_chapters_014 import SUPPORT
folder=ROOT/'work/translation/en/chapters_0.1.14';notes=json.loads((folder/'optional_ch78_review_notes.json').read_text());expected=[n for n in SUPPORT if 204<=n<=242];assert sorted(map(int,notes))==expected
count=0;fixcount=0;examined=0
for number in expected:
 _,rows,data=load(number);local=folder/f'{number:04d}';note=notes[str(number)]
 report={'resource_id':f'00:{number:05d}','review_type':'independent_meaning_review','semantic_complete':True,'reviewed_rows':list(range(11,len(rows))),'reviewed_slices':[],'corrections':[],'uncertainties':note['uncertainties'],'rows_examined':{'physical_ranges_inclusive':[[0,len(rows)-1]],'count':len(rows)},'method':'Independent reviewer read each target against the original Japanese and the full local conversation. Scope covers only physical dialogue rows 11 onward; first eleven system rows examined as context, not included in semantic coverage. Consecutive target slices have at most 80 rows. Acceptable variants left unchanged; corrections focus on meaning. No machine translation service used.'}
 seen=[]
 for p in sorted(local.glob('slice_*.targets.json')):
  d=json.loads(p.read_text());ns=sorted(t['resource_row'] for t in d['translations'].values());assert len(ns)<=80
  report['reviewed_slices'].append({'target_file':str(p.relative_to(ROOT)).replace('\\','/'),'target_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'assigned_range':[ns[0],ns[-1]],'translation_count':len(ns)})
  seen+=ns
 assert seen==report['reviewed_rows']
 for key,text in note['corrections'].items():
  n=int(key);r=rows[n];src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');encode_dialogue(text,src);assert control_tokens(text)==control_tokens(src)
  report['corrections'].append({'resource_row':n,'source_sha256':r['source_sha256'],'text':text})
 print(json.dumps({'resource':number,'reviewed_rows':len(seen),'source_rows_examined':len(rows),'corrections':report['corrections']},ensure_ascii=False))
 count+=len(seen);examined+=len(rows);fixcount+=len(report['corrections'])
 if '--write' in sys.argv:(local/'independent_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'resources':len(expected),'reviewed_rows':count,'source_rows_examined':examined,'corrections':fixcount,'mode':'write' if '--write' in sys.argv else 'dry-run'}))
