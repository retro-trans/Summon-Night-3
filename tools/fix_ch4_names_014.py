import json,sys
from pathlib import Path
folder=Path('work/translation/en/chapters_0.1.14/0134')
changes=[]
for p in folder.glob('slice_*.targets.json'):
 d=json.loads(p.read_text());dirty=False
 for t in d['translations'].values():
  old=t['text'];new=old.replace('Master Mimic','Mimic Master').replace('MASTER MIMIC','MIMIC MASTER').replace('Urgola','Ulgorla')
  if old!=new:changes.append([t['resource_row'],old,new]);t['text']=new;dirty=True
 if dirty and '--write' in sys.argv:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(changes,indent=2))
