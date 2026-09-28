import sys,json
from pathlib import Path
sys.path.insert(0,'tools')
from chapter_source_014 import load,ROOT
_,rows,data=load(134)
terms=[('ウルゴーラ','Ulgorla','place','English wiki explicitly names the imperial capital in the Inherited Flames story; root researched.','https://summonnight.fandom.com/wiki/Summon_Night_3_~_Inherited_Flames'),('集いの泉','Gathering Spring','place','Provisional translation; Japanese name confirmed in walkthrough.','https://w.atwiki.jp/sn3psp/pages/18.html'),('バウナス','Bawnas','creature_species','Provisional romanization. Panashe describes own species; no gender inferred from the name.',None),('トライドラ','Lendora','place_and_sword_style','English wiki names the city where Forte trained with Shamrock Lendora; contextual mapping to Japanese Tridora, not directly bilingual-attested.','https://summonnight.fandom.com/wiki/Forte')]
entries=[]
for jp,en,cat,note,url in terms:
 found=[]
 for n,r in enumerate(rows[1808:],1808):
  if jp in data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932'):found.append({'source_id':r['id'],'source_physical_row':n})
 e={'source_name':jp,'target_name':en,'category':cat,'status':'wiki_confirmed' if en=='Ulgorla' else 'provisional','notes':note,'evidence':found}
 if url:e['evidence'].append({'url':url,'researcher':'root'})
 if jp=='トライドラ':e['evidence'].append({'url':'https://w.atwiki.jp/storytellermirror/pages/608.html','supports':'Japanese city name in same Forte/Shamrock history; root research'})
 entries.append(e)
doc={'schema_version':1,'language':'en','version':'0.1.14','entries':entries}
print(json.dumps(doc,ensure_ascii=False,indent=2))
if '--write' in sys.argv:(ROOT/'work/glossary/chapter4_provisional_0.1.14.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
