import json,sys
from pathlib import Path
from chapter_source_014 import load,ROOT
for number in map(int,sys.argv[1:]):
 _,rows,data=load(number);folder=ROOT/f'work/translation/en/chapters_0.1.14/{number:04d}';ts={t['resource_row']:t for p in folder.glob('slice_*.targets.json') for t in json.loads(p.read_text())['translations'].values()}
 print('RESOURCE',number,'rows',len(rows),'targets',len(ts))
 for n,r in enumerate(rows):
  src=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');print(n,src,'=>',ts.get(n,{}).get('text','[context only]'))
