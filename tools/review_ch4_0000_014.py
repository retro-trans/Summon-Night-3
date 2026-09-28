import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,'tools')
from chapter_source_014 import load,ROOT
from dialogue_encoding import encode_dialogue,control_tokens
folder=ROOT/'work/translation/en/chapters_0.1.14/0134'
_,rows,data=load(134);rows=rows[1808:]
fix={6:'As for the lumber we cut,',7:'I trimmed off all the branches,',8:'just as you asked.',33:'of my home in the countryside...',61:'Drinking that',62:'quickly is bad for you...',64:'Drinking that',65:'quickly is bad for you...',83:"So that's why you were dehydrated.",157:'No, even they',158:"didn't have those...",163:'said she was good',164:"with guns, didn't she?"}
report={'resource_id':'00:00134','review_type':'independent_meaning_review','semantic_complete':True,'reviewed_slices':[],'corrections':[],'uncertainties':[{'resource_rows':[165,166],'note':'She dropped it retained: neighboring remark and Sonolar reply support another speaker referring to her.'}],'method':'Independently read all 240 source rows alongside earlier targets with eight context rows before and after the scope. Corrected harmful-versus-poison mistranslation, omitted hometown nuance, unclear gun-shop reply, and referent clarity; left acceptable alternatives unchanged.'}
for start in (0,80,160):
 p=folder/f'slice_{start:04d}.targets.json';report['reviewed_slices'].append({'target_file':str(p.relative_to(ROOT)).replace('\\','/'),'target_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'assigned_range':[start,start+79],'translation_count':80,'rows_examined':{'physical_ranges_inclusive':[[1800,2055]],'count':256}})
for n,text in fix.items():
 r=rows[n];src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');encode_dialogue(text,src);assert control_tokens(text)==control_tokens(src)
 report['corrections'].append({'resource_row':n,'id':r['id'],'source_sha256':r['source_sha256'],'text':text})
print(json.dumps(report,indent=2))
if '--write' in sys.argv:(folder/'review_meaning_0000_0239.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
