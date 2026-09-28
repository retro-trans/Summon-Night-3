"""Regression checks against the released crashing stance records."""
import json,struct
from stance_028 import *

def verify():
 with GameSource(BASE/'Summon_Night_3_EN_0.1.27.iso') as s:
  changes,_,master,report=prepare_tables(s)
  old=s.resource('02.DAT',3);oldtb=child(old,parse_index(old,len(old)),31)
  new=changes[3];tb=child(new,parse_index(new,len(new)),31)
  assert child(master,parse_index(master,len(master)),7)==new
  detected=[]
  for e in report['tables'][0]['changes']:
   rows,end=lines_at(tb,e['new_offset']);assert tb[end:end+2]==b'\0\0';assert len(rows)<=2;glyph_check(rows)
   assert all(struct.unpack_from('<I',tb,f)[0]==e['new_offset'] for f in e['pointer_fields'])
   try:glyph_check(lines_at(oldtb,e['previous_offset'])[0])
   except AssertionError:detected.append(e['record'])
  assert 100 in detected and 101 in detected
  assert prepare_elf()[0]==(BASE/'EBOOT.elf').read_bytes()
  return dict(records_checked=len(report['tables'][0]['changes']),old_invalid_records=detected,executable_unchanged=True,resident_mirror_identical=True)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
