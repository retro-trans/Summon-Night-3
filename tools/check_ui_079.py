"""Validate active attack UI fields against the real help staging capacity."""
import json,struct,unicodedata
from sn3_archive import ROOT,GameSource,parse_index,child
from menu_hotfix_017 import lines_at
from dialogue_encoding import encode_dialogue

def check(static,targets=None):
 b=child(static,parse_index(static,len(static)),25)
 overrides={f:e['english'] for e in (targets or {}).get('entries',[]) for f in e['pointer_fields']}
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 issues=[];rows=[]
 for r in range(struct.unpack_from('<I',b)[0]):
  if targets and not any(4+r*48+slot*4 in overrides for slot in (8,9,10)):continue
  if r<24:continue # Native basic attack labels use separately delimited single strings.
  texts={}
  for slot in (8,9,10):
   f=4+r*48+slot*4;p=struct.unpack_from('<I',b,f)[0]
   raw=lines_at(b,p)[0] if p else []
   if slot==8:raw=raw[:1]
   texts[slot]=overrides.get(f,[unicodedata.normalize('NFKC',x.decode('cp932')) for x in raw])
  name=texts[8][0] if texts[8] else ''
  help=texts[9]+texts[10]
  if help and (len(help)>3 or max(map(len,help))>27 or sum(map(len,help))>54):issues.append([r,help])
  if name and all(c in metrics for c in name):
   width=sum(metrics[c]['proposed_advance_pixels'] for c in name)*.875
   if width>140:issues.append([r,'name width',name,width])
  rows.append(dict(record=r,name=name,help=help))
 return dict(passed=not issues,issues=issues,rows=rows)

if __name__=='__main__':
 with GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as s:
  r=check(s.resource('02.DAT',3),json.loads((ROOT/'work/translation/en/ui_0.1.79/targets.json').read_text()))
 print(json.dumps(dict(passed=r['passed'],issues=r['issues']),indent=2))
