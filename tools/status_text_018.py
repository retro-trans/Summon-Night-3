"""Source-bound status names and fixed-width labels; pure prepare functions."""
import json,struct,hashlib,unicodedata
import battle_elf_patch as patcher
from battle_table_patch import relocate_fullwidth
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from character_labels import collect
from menu_hotfix_017 import lines_at,glyph_check

BASE=ROOT/'work/output/0.1.17'
FOLDER=ROOT/'work/translation/en/status_0.1.18'
sha=lambda b:hashlib.sha256(b).hexdigest()

def load_targets(name,limit):
 rows=json.loads((FOLDER/(name+'.targets.json')).read_text())['translations']
 for identity,r in rows.items():
  text=r.get('compact') or r['text']
  assert text and text.isascii() and len(text)<=limit,(identity,text)
  assert not any(c in text for c in '\0\r\n')
  assert 'unresolved' not in r.get('status','').lower(),identity
 return rows

def prepare_elf():
 m=json.loads((BASE/'manifest.json').read_text());idx=patcher.indexed_rows()
 target=dict(idx['elf:ui:0021944c'],target_full='None')
 previous=patcher.BASELINE
 try:
  patcher.BASELINE=BASE/'EBOOT.elf'
  data,report=patcher.prepare(patcher.BASELINE.read_bytes(),[target],idx)
 finally:patcher.BASELINE=previous
 assert not report['skipped']
 out=bytearray(data);changes=[]
 choices={0x2176fc:'VSlash',0x217704:'HSlash',0x21772c:'Spec.',0x217734:'VThrow',0x21773c:'HThrow'}
 for e in m['menu_text']['entries']:
  if e['source_offset'] not in choices:continue
  text=choices[e['source_offset']];pos=e['new_file_offset'];span=e['encoded_bytes']
  assert out[pos:pos+span]==e['display_text'].encode('cp932')+b'\0\0'
  encoded,display=encode_dialogue(text,'');assert len(text)<=6 and len(encoded)+2<=span
  out[pos:pos+span]=encoded+bytes(span-len(encoded))
  changes.append(dict(id=e['id'],text=text,display_text=display,new_file_offset=pos,span=span))
 assert len(changes)==5
 # Preserve every 0.1.17 crash fix byte for byte and recheck its capacity.
 for e in m['menu017_hotfix']['changes']:
  pos=e['new_file_offset'];span=e['span']
  assert out[pos:pos+span]==(BASE/'EBOOT.elf').read_bytes()[pos:pos+span]
  glyph_check(lines_at(out,pos)[0])
 report.update(profile='status_0.1.18',compact_attacks=changes,retained_crash_fixes=5)
 return bytes(out),report

def prepare_tables(source):
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 gear=load_targets('gear',15);magic=load_targets('magic',15);weapons=load_targets('weapon_review',15)
 assert not gear.keys()&magic.keys()
 targets={**gear,**magic};overrides=[]
 for identity,row in weapons.items():
  if identity in targets:
   assert identity.startswith('02:00003/00015:') and row['source_sha256']==targets[identity]['source_sha256']
   overrides.append(dict(id=identity,before=targets[identity]['text'],after=row['text']))
  targets[identity]=row
 static=source.resource('02.DAT',3);si=parse_index(static,len(static));replacements={};reports=[]
 for table in idx['tables']:
  selected={r['id']:dict(text=targets[r['id']].get('compact') or targets[r['id']]['text'],source_sha256=targets[r['id']]['source_sha256']) for r in table['strings'] if r['id'] in targets}
  if not selected:continue
  n=table['resource_path'][1];before=child(static,si,n)
  starts={r['id']:selected[r['id']] for r in table['strings'] if r['id'] in selected and r['references']}
  assert len(starts)==len(selected),'Name target is not a direct pointer'
  after,changes,skipped=relocate_fullwidth(before,table['strings'],starts,selected)
  # Already translated targets must resolve to an actual English string.
  byid={r['id']:r for r in table['strings']}
  for skipped_row in skipped:
   row=byid[skipped_row['id']]
   for ref in row['references']:
    pointer=struct.unpack_from('<I',before,ref['pointer_field_offset'])[0]
    raw=before[pointer:before.index(b'\0',pointer)].decode('cp932')
    normalized=unicodedata.normalize('NFKC',raw)
    assert normalized and normalized.isascii() and normalized.isprintable(),(row['id'],raw)
   skipped_row['validated_existing_english']=True
  replacements[n]=after;reports.append(dict(child=n,changes=changes,skipped=skipped))
 # Defense labels share a fixed width status field: five native glyphs.
 m=json.loads((BASE/'manifest.json').read_text());out=bytearray(child(static,si,31));defenses=[]
 for table in m['battle_tables']['tables']:
  for e in table['changes']:
   if e['text'] not in ('Defend','Counter'):continue
   text={'Defend':'Guard','Counter':'Cntr'}[e['text']];pos=e['new_offset'];span=e['new_byte_length']+2
   assert out[pos:pos+span]==e['display_text'].encode('cp932')+b'\0\0'
   encoded,_=encode_dialogue(text,'');assert len(text)<=5 and len(encoded)+2<=span
   out[pos:pos+span]=encoded+bytes(span-len(encoded));defenses.append(dict(id=e['id'],text=text,new_offset=pos,span=span))
 assert len(defenses)==2
 replacements[31]=bytes(out);patched_static=repack(static,replacements)
 labels,_,rows=collect(source);out=bytearray(labels);units=load_targets('unit',10);unit_changes=[]
 for row in rows:
  if row['id'] not in units:continue
  t=units[row['id']];assert t['source_sha256']==row['source_sha256']
  text=t.get('compact') or t['text'];encoded,display=encode_dialogue(text,'')
  out.extend(bytes(-len(out)%2));pos=len(out);out.extend(encoded+b'\0\0')
  for r in row['references']:
   assert struct.unpack_from('<I',out,r['pointer_field_offset'])[0]==row['source_offset']
   struct.pack_into('<I',out,r['pointer_field_offset'],pos)
  unit_changes.append(dict(id=row['id'],text=text,full=t['text'],new_offset=pos,display_text=display,references=row['references']))
 assert len(unit_changes)==len(units)
 bank01=repack(source.resource('01.DAT',1),{0:bytes(out)})
 master=source.resource('00.DAT',44);mi=parse_index(master,len(master));assert child(master,mi,7)==static
 cached=child(master,mi,6);ci=parse_index(cached,len(cached));assert child(cached,ci,0)==labels
 master=repack(master,{6:repack(cached,{0:bytes(out)}),7:patched_static})
 return {3:patched_static},{1:bank01},master,dict(tables=reports,units=unit_changes,compact_defenses=defenses,reviewed_weapon_overrides=overrides)
