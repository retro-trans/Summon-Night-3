"""Read at most 80 target rows plus source context, without saving transcripts."""
import argparse,json
from chapter_source_014 import load
from sn3_archive import ROOT
p=argparse.ArgumentParser();p.add_argument('number',type=int);p.add_argument('start',type=int);p.add_argument('--count',type=int,default=80);a=p.parse_args();assert 1<=a.count<=80
r,rows,d=load(a.number);shift=1808 if a.number in (134,157) else 3957 if a.number in (180,203,226) else 0
ts={v['resource_row']:v['text'] for q in (ROOT/f'work/translation/en/chapters_0.1.14/{a.number:04d}').glob('slice_*.targets.json') for v in json.loads(q.read_text(encoding='utf-8'))['translations'].values()}
end=min(a.start+a.count,len(rows)-shift)
print('RESOURCE',a.number,'ASSIGNED',a.start,end-1,'EXAMINED',max(0,a.start-5),min(len(rows)-shift-1,end+4))
for n in range(max(0,a.start-5),min(len(rows)-shift,end+5)):
 x=rows[n+shift];src=d[x['source_offset']:x['source_offset']+x['source_byte_length']].decode('cp932');print(n,src,'|',ts.get(n,'<not drafted>'))
