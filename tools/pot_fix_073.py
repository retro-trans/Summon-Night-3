"""Safely load cached summon names and discard impossible saved bindings."""
import struct,hashlib
from sn3_archive import ROOT
from menu_code_020 import append
from pot_fix_072 import prepare_elf as prior_prepare,prepare_names
from stages_pupil_names import validate_loader_structure
BASE=ROOT/'work/output/0.1.72'
ACCESSORY_COUNT=121
def emit(a):
 a.label('load_name');a.move('t0','a0');a.move('t1','a1');a.i(9,'t2','zero',9)
 a.label('load_cell');a.i(37,'t3','t1',0);a.branch(4,'t3','zero','load_done')
 a.i(41,'t3','t0',0);a.i(9,'t0','t0',2);a.i(9,'t1','t1',2)
 a.i(9,'t2','t2',-1);a.branch(5,'t2','zero','load_cell')
 a.label('load_done');a.i(41,'zero','t0',0);a.move('v0','a0');a.ret()
 a.label('load_fields');a.i(37,'a0','s5',0x693a);a.i(36,'a1','s4',0x693c)
 a.i(11,'t0','a0',ACCESSORY_COUNT);a.branch(5,'t0','zero','fields_valid')
 a.move('a0','zero');a.move('a1','zero')
 a.label('fields_valid');a.i(41,'a0','s0',0xc48);a.i(41,'a1','s0',0xc4a)
 a.move('a0','zero');a.ret()
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();assert old==prior_prepare()[0]
 # Accessory IDs are direct indices in the immutable 121-entry table.
 from sn3_archive import GameSource,parse_index,child
 with GameSource(BASE/'Summon_Night_3_EN_0.1.72.iso') as source:
  static=source.resource('02.DAT',3);t=child(static,parse_index(static,len(static)),17)
  assert struct.unpack_from('<I',t)[0]==ACCESSORY_COUNT
 hooks={0x629ac:('load_name',3<<26|0x1c2b80>>2),0x629b4:('load_fields',0x96a4693a)}
 out,r=append(old,emit,hooks);out=bytearray(out)
 # The helper replaces both saved-field loads/stores and restores a0=0,
 # the native counter for the following four ability flags.
 expected={0x629b8:0xa6040c48,0x629bc:0x9285693c,0x629c0:0x34040000,0x629c4:0x30a500ff,0x629c8:0xa6050c4a}
 for at,w in expected.items():
  assert struct.unpack_from('<I',old,at+192)[0]==w,(hex(at),hex(struct.unpack_from('<I',old,at+192)[0]))
  struct.pack_into('<I',out,at+192,0)
 out=bytes(out);r.update(source_sha256=hashlib.sha256(old).hexdigest(),output_sha256=hashlib.sha256(out).hexdigest(),
  accessory_count=ACCESSORY_COUNT,save_record_bytes_unchanged=True,invalid_binding_policy='Reset only IDs outside 0..120, along with their binding flag',
  structure=validate_loader_structure(out))
 return out,r
