"""Validate every equipment output against the two-line UI and native pool."""
import json,struct,unicodedata
from sn3_archive import ROOT,child,parse_index
from menu_hotfix_017 import lines_at
from verify_equipment_047 import CPU
from verify_guards_049 import AliasCPU,stage
from inventory_050 import BASE,TARGETS

def verify(elf,static):
 cfg=json.loads(TARGETS.read_text());old=(BASE/'EBOOT.elf').read_bytes();checks=[];changed=[];renderer=AliasCPU(elf,static)
 for kind in range(3):
  c=CPU(elf,static,kind);b=CPU(old,static,kind)
  for rec in range(1,c.count):
   for key in (False,True):
    c.mem[0x6ffc80:0x6ffcc0]=b'G'*64
    prior=b.run(rec,key);r=c.run(rec,key)
    assert c.r[29]==0x700000 and c.mem[0x6ffc80:0x6ffcc0]==b'G'*64,'stack bounds'
    assert len(r['lines'])<=2 and max(r['lengths'],default=0)<=27 and r['total']<=54,(kind,rec,key,r)
    if len(prior['lines'])<=2:assert r['lines']==prior['lines'],(kind,rec,key)
    else:
     expected=' '.join(' '.join(prior['lines']).split())
     for x,y in cfg['help_compaction'].items():expected=expected.replace(x,y)
     assert ''.join(expected.split())==''.join(''.join(r['lines']).split()),(kind,rec,key,expected,r)
     changed.append(dict(kind=kind,record=rec,key_item=key,before=prior['lines'],after=r['lines']))
    if kind==0 and rec==26 and not key:
     assert r['lines'][0]==prior['lines'][0] and 'Blind Hit30%' in r['lines'][1],r
    staged=stage(renderer,c.mem[0x5019f0:0x5019f0+178]);assert staged['rows']<=2 and staged['max_slot']<54
    checks.append(r)
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());rows=next(t['strings'] for t in index['tables'] if t['resource_path']==[3,15]);table=child(static,parse_index(static,len(static)),15);names=[]
 for row in rows:
  for ref in row['references']:
   ptr=struct.unpack_from('<I',table,ref['pointer_field_offset'])[0];raw=lines_at(table,ptr)[0][0];text=unicodedata.normalize('NFKC',raw.decode('cp932'))
   assert text.isascii() and len(raw)//2<=15,(row['id'],text)
   names.append(text)
 for e in cfg['entries']:
  row=next(r for r in rows if r['id']==e['id'])
  for ref in row['references']:
   p=struct.unpack_from('<I',table,ref['pointer_field_offset'])[0]
   assert unicodedata.normalize('NFKC',lines_at(table,p)[0][0].decode('cp932'))==e['text']
 return dict(equipment_cases=len(checks),changed=changed,max_rows=max(len(r['lines']) for r in checks),max_cells=max(r['total'] for r in checks),weapon_references=len(names),translated_names=len(cfg['entries']),all_weapon_names_english=True)
