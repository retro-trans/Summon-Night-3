"""Armor translations and omitted symbolic stat prefixes on immutable 0.1.50."""
import json,struct,hashlib
from sn3_archive import ROOT,parse_index,child
from sn3_repack import repack
from dialogue_encoding import encode_dialogue
from menu_code_020 import append
from font_patch import REG
BASE=ROOT/'work/output/0.1.50'
TARGETS=ROOT/'work/translation/en/armor_0.1.51/targets.json'
HOOK=0x642c0
# The native font uses these CP932 box-drawing cells as stat labels.
STAT_CELLS=(0xaa84,0xac84)
sha=lambda b:hashlib.sha256(b).hexdigest()

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();word=struct.unpack_from('<I',old,HOOK+192)[0]
 assert word>>26==3
 prior=(word&0x3ffffff)<<2
 def emit(a):
  a.label('armor_stat_dispatch');a.i(35,'t0','s4',0x34);a.i(9,'t1','zero',6)
  a.branch(5,'t0','t1','prior')
  a.i(37,'t0','s4',0x4c)
  for cell in STAT_CELLS:
   a.i(13,'t1','zero',cell);a.branch(4,'t0','t1','native')
  a.label('prior');a.jump(prior,link=False)
  a.label('native');a.emit(REG['a2']<<21|8);a.emit(0)
 out,report=append(old,emit,{HOOK:('armor_stat_dispatch',word)})
 report.update(entries=[],previous_target=hex(prior),stat_cells=[hex(c) for c in STAT_CELLS],rule='Mode 6 starting with native 84aa or 84ac stat cell uses original position callback; every other row retains prior dispatch.')
 return out,report

def prepare_tables(source):
 cfg=json.loads(TARGETS.read_text());idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());rows={r['id']:r for t in idx['tables'] if t['resource_path']==[3,16] for r in t['strings']}
 static=source.resource('02.DAT',3);before=child(static,parse_index(static,len(static)),16);out=bytearray(before);fields=set();changes=[]
 for e in cfg['entries']:
  row=rows[e['id']];p=row['source_offset'];n=row['source_byte_length'];assert sha(before[p:p+n])==e['source_sha256']
  raw=encode_dialogue(e['text'],'')[0];assert len(raw)//2<=15
  out.extend(bytes(-len(out)%2));new=len(out);out.extend(raw+b'\0\0\0\0')
  for ref in row['references']:
   f=ref['pointer_field_offset'];assert struct.unpack_from('<I',before,f)[0]==p
   struct.pack_into('<I',out,f,new);fields.update(range(f,f+4))
  changes.append(dict(e,new_offset=new,references=row['references']))
 assert all(a==b or i in fields for i,(a,b) in enumerate(zip(before,out)))
 patched=repack(static,{16:bytes(out)});master=source.resource('00.DAT',44);assert child(master,parse_index(master,len(master)),7)==static
 return {3:patched},{},repack(master,{7:patched}),dict(units=[],tables=[dict(child=16,changes=changes)],gameplay_fields_unchanged=True)

def verify(elf,static):
 from verify_armor_051 import verify as run
 return run(elf,static)
