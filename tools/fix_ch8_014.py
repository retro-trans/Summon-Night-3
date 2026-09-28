"""Chapter 8 author self-check corrections; dry-run by default."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'work/translation/en/chapters_0.1.14/0226'
replacements={'a chosen bearer':'one of the Qualified','A chosen bearer':'One of the Qualified','Azure Sage Emperor':'Azure Sage','Kilsres':'Crissles','Yucres Village':'Yukres Village','Wind and Thunder Settlement':'Land of Wind and Thunder','Lord Falzen':'Falzen'}
exact={982:' Really believe that?',985:' Really believe that?',2148:' That is reassuring.',2150:' That is reassuring.',155:'Is that Shartos, the sword',499:'kept in their trouser pocket',512:'their friends.',537:'the pointy-eared one went',540:'the pointy-eared one went',2239:'That I started the fire...'}
changes=[]
for p in sorted(folder.glob('slice_*.targets.json')):
 d=json.loads(p.read_text(encoding='utf-8'))
 for t in d['translations'].values():
  old=t['text'];new=old
  for a,b in replacements.items():new=new.replace(a,b)
  if t['resource_row'] in exact:new=exact[t['resource_row']]
  if old!=new:changes.append({'row':t['resource_row'],'before':old,'after':new});t['text']=new
 if '--write' in sys.argv:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'mode':'write' if '--write' in sys.argv else 'dry-run','changes':changes},ensure_ascii=False,indent=2))



