import json,sys
from pathlib import Path
fix={1963:'WANT ME TO STOP?',1968:'COPYING TO THE END,',1980:'FOR YOUR EFFORT,',1984:'SO PITIFUL...',1985:'I COULD WEEP!',1989:'TO MASTER'}
p=Path('work/translation/en/chapters_0.1.14/0134/slice_1920.targets.json');d=json.loads(p.read_text())
for t in d['translations'].values():
 n=t['resource_row']
 if n in fix:print(n,t['text'],'=>',fix[n]);t['text']=fix[n]
if '--write' in sys.argv:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
