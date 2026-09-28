"""Finalize reviewed battle terminology and two contextual corrections."""
import argparse,json
from battle_source_024 import ROOT,load,sha,source_text
from battle_compiler_024 import targets
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
fixes={164:'You little rascal!?',718:"I've heard about you from my student.",760:"A tool spirit? ...No, that's not it."}
_,rows,data=load(175)
corrections=[dict(resource=175,resource_row=n,source_sha256=rows[n]['source_sha256'],text=t,reason='Final source-context adjudication: descriptive nickname, unspecified gender, and descriptive spirit category.') for n,t in fixes.items()]
bindings={}
for n in (160,640,720):
 f=ROOT/f'work/translation/en/battle_0.1.24/common_{n:04d}.targets.json';bindings[str(f.relative_to(ROOT)).replace('\\','/')]=sha(f.read_bytes())
review=dict(review_kind='final_context_adjudication',draft_inputs_sha256=bindings,corrections=corrections)
for n in (155,156):
 _,rr,dd=load(n);tt,_=targets(n,rr,dd)
 for k,r in enumerate(rr):print(n,k,source_text(r,dd),'=>',tt[k]['text'])
glossary=dict(version='0.1.24',reference='https://summonnight.fandom.com/wiki/Summon_Night_6:_Lost_Borders/PS_Vita_Gallery',policy='Normalize names after meaning review. Preserve Ness as the source nickname for Nesty.',aliases={'Tris':'Toris','Leold':'Le-O-LD','Recie':'Resi','Amel':'Amer','Rocka':'Rocca','Ryugu':'Ruug','Minith':'Minis','Sonora':'Sonolar','Alize':'Alieze','Arumine':'Almine','Golden Faction':'Gold Faction','Sapress':'Sapureth'})
print(json.dumps(review,indent=2));print(json.dumps(glossary,indent=2))
if a.write:
 (ROOT/'work/translation/en/battle_0.1.24/review_zz_final.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf8')
 (ROOT/'work/glossary/battle_0.1.24.json').write_text(json.dumps(glossary,indent=2)+'\n',encoding='utf8')
