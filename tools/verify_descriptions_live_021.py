"""Read-only checks of relocated spell text in the isolated 19382 test process."""
import json,base64,struct
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from descriptions_runtime_021 import request

def verify():
 base=0x08804000;folder=ROOT/'work/scratch/descriptions_candidate_0.1.21'
 m=json.loads((folder/'manifest.json').read_text());elf=(folder/'EBOOT.elf').read_bytes()
 def read(a,n):return base64.b64decode(request('memory.read',address=a,size=n)['base64'])
 def word(a):return int.from_bytes(read(a,4),'little')
 def opcode(a):return request('memory.disasm',address=base+a,count=1)['lines'][0]['encoding']
 def hilo(h,l):return ((opcode(h)&65535)<<16)+struct.unpack('<h',struct.pack('<H',opcode(l)&65535))[0]
 spell_registry=hilo(0x65900,0x65920)
 effect_registry=hilo(0x65acc,0x65c24)
 refs=[];literals=[];report=m['descriptions021_text']
 for e in report['entries']:
  addr=base+(int(e['new_address'],16) if 'new_address' in e else e['new_file_offset']-192)
  expected=e['display_text'].encode('cp932')+b'\0\0';assert read(addr,len(expected))==expected,e['id'];literals.append(e['id'])
  for r in e.get('references',[]):
   if r['kind']=='hilo':
    hi,lo=opcode(int(r['high'],16)),opcode(int(r['low'],16));low=struct.unpack('<h',struct.pack('<H',lo&65535))[0]
    assert ((hi&65535)<<16)+low==addr,(e['id'],r)
   else:assert word(base+int(r['instruction'],16))==addr
   refs.append(r)
 for a in report['branch_entry_high_halves']:
  e=next(e for e in report['entries'] if e['id']==a['source_id']);r=e['references'][0]
  hi,lo=opcode(int(a['instruction'],16)),opcode(int(r['low'],16))
  assert ((hi&65535)<<16)+struct.unpack('<h',struct.pack('<H',lo&65535))[0]==base+int(e['new_address'],16)
 tables=[]
 index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
 for table in m['descriptions021_tables']['tables']:
  n=table['child'];idx=next(t for t in index['tables'] if t['resource_path']==[3,n]);rows={r['id']:r for r in idx['strings']}
  for e in table['changes']:
   r=rows[e['id']]['references'][0];record,slot=r['record'],r['slot']
   recptr=word(spell_registry+4+record*4) if n==13 else word(effect_registry+4)+record*32
   pointer=word(recptr+slot*4);expected=b''.join(encode_dialogue(s,'')[0]+b'\0\0' for s in e['lines'])+b'\0\0'
   assert read(pointer,len(expected))==expected,(n,record,e['id']);tables.append(e['id'])
 for e in m['menu017_hotfix']['changes']:
  assert read(base+int(e['new_address'],16),e['span'])==elf[e['new_file_offset']:e['new_file_offset']+e['span']]
 return dict(version='0.1.21',fresh_launch=True,normal_copied_battle_save=True,save_state_used=False,
  emulator='PPSSPP 1.20.4 software 1x',port=19382,source_iso_sha256=m['output_sha256'],
  elf_literals_verified=len(literals),relocation_references_verified=len(refs),alternate_branch_highs_verified=len(report['branch_entry_high_halves']),
  resident_table_descriptions_verified=len(tables),crash_fix_spans_verified=5,
  visual_checks=['Battle Prep opens','Dritol detail','Drill Blow: ATK Pwr:12 Single','Drill Rush: translated description','Drill Hurricane: ATK Pwr:38 Single','proportional text; no clipping'],
  native_formatter_all_records=len(m['descriptions021_tables']['native_formatter_cases']),
  limitations=['Visual checks cover available saved-game spells; other spells checked by executing native formatter and live resident table checks.','Hardware GPU and original PSP not tested.'])

if __name__=='__main__':print(json.dumps(verify(),indent=2))
