"""Validate all menu-help roots and translated generic unit-name pointers."""
import json,struct,unicodedata
from menu_enemy_035 import prepare_elf,prepare_tables,BASE
from sn3_archive import ROOT,GameSource,parse_index,child
from stages_pupil_names import parse_elf
from battle_elf_refs import references
from battle_elf_patch import indexed_rows
from menu_hotfix_017 import lines_at
from character_labels import collect

def verify():
 data,r=prepare_elf();ph=parse_elf(data)['phdrs'];original=(ROOT/'work/source/EBOOT.elf').read_bytes();refs,_,_=references(original)
 def offset(va):return next(p[1]+va-p[2] for p in ph if p[0]==1 and p[2]<=va<p[2]+p[4])
 checked=[]
 for row in indexed_rows().values():
  off=row['source_offset'];va=off-192
  if not 0x217bb8<=off<=0x218274 or va not in refs:continue
  for ref in refs[va]:
   assert ref['kind']=='pointer'
   ptr=struct.unpack_from('<I',data,ref['address']+192)[0]
   lines,end=lines_at(data,offset(ptr));texts=[unicodedata.normalize('NFKC',s.decode('cp932')) for s in lines]
   assert all(t.replace('’',"'").isascii() for t in texts),(row['id'],texts)
   assert len(lines)<=2 and all(len(s)//2<=27 for s in lines) and sum(len(s)//2 for s in lines)<=54,(row['id'],texts)
   checked.append(dict(id=row['id'],lines=texts,pointer=hex(ref['address'])))
 with GameSource(BASE/'Summon_Night_3_EN_0.1.34.iso') as s:
  _,p01,master,t=prepare_tables(s);old,_,rows=collect(s)
  bank=p01[1];new=child(bank,parse_index(bank,len(bank)),0)
  cached=child(master,parse_index(master,len(master)),6);assert new==child(cached,parse_index(cached,len(cached)),0)
  changed={ref['pointer_field_offset'] for e in t['units'] for ref in e['references']}
  for row in rows:
   for ref in row['references']:
    f=ref['pointer_field_offset']
    if f not in changed:assert old[f:f+4]==new[f:f+4]
  assert all(old[n]==new[n] for n in range(len(old)) if not any(f<=n<f+4 for f in changed))
  assert next(e['text'] for e in t['units'] if e['id']=='char_label:000079d6')=='Pirate'
 return dict(new_help_groups=len(r['entries']),all_help_references_checked=len(checked),help=checked,enemy_labels=len(t['units']),enemy_pointer_references=len(changed),unselected_labels_unchanged=True,original_string_pool_unchanged=True,resident_bank_copies_match=True)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
