"""Keep full summon names outside the native 20-byte name/animation record."""
import struct,hashlib
from sn3_archive import ROOT
from menu_code_020 import append
from stages_pupil_names import parse_elf,validate_loader_structure
BASE=ROOT/'work/output/0.1.70'
SLOTS=256
STRIDE=68
CAPACITY=64
sha=lambda b:hashlib.sha256(b).hexdigest()
def emit(a):
 # Each slot has the native destination key and 64 bytes of display text.
 # No native record, save layout, or animation field is enlarged.
 a.label('copy_name');a.table_address('t0');a.i(9,'t1','zero',SLOTS)
 a.label('copy_find');a.i(35,'t2','t0',0)
 a.branch(4,'t2','a0','copy_slot');a.branch(4,'t2','zero','copy_slot')
 a.i(9,'t0','t0',STRIDE);a.i(9,'t1','t1',-1);a.branch(5,'t1','zero','copy_find')
 # All 88 native destinations fit; retain a bounded fallback defensively.
 a.move('t6','a1');a.branch(4,'zero','zero','copy_cache')
 a.label('copy_slot');a.i(43,'a0','t0',0);a.i(9,'t6','t0',4)
 # Clear the display slot so short replacements cannot retain old suffixes.
 a.move('t3','t6');a.i(9,'t4','zero',32)
 a.label('copy_clear');a.i(41,'zero','t3',0);a.i(9,'t3','t3',2)
 a.i(9,'t4','t4',-1);a.branch(5,'t4','zero','copy_clear')
 a.move('t3','t6');a.move('t4','a1');a.i(9,'t5','zero',31)
 a.label('copy_full');a.i(37,'t7','t4',0);a.branch(4,'t7','zero','copy_full_done')
 a.i(41,'t7','t3',0);a.i(9,'t3','t3',2);a.i(9,'t4','t4',2)
 a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','copy_full')
 a.label('copy_full_done');a.i(41,'zero','t3',0)
 # Native names may be right-padded with full-width spaces.
 a.i(13,'t8','zero',0x4081)
 a.label('copy_trim');a.branch(4,'t3','t6','copy_cache')
 a.i(37,'t7','t3',-2);a.branch(5,'t7','t8','copy_cache')
 a.i(9,'t3','t3',-2);a.i(41,'zero','t3',0);a.branch(4,'zero','zero','copy_trim')
 a.label('copy_cache');a.move('t3','a0');a.move('t4','t6');a.i(9,'t5','zero',9)
 a.label('copy_short');a.i(37,'t7','t4',0);a.branch(4,'t7','zero','copy_done')
 a.i(41,'t7','t3',0);a.i(9,'t3','t3',2);a.i(9,'t4','t4',2)
 a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','copy_short')
 a.label('copy_done');a.i(41,'zero','t3',0);a.move('v0','a0');a.ret()
 a.label('get_name');a.emit(5<<16|8<<11|5<<6) # sll t0,a1,5
 a.emit(4<<21|8<<16|2<<11|0x21);a.i(9,'v0','v0',0xc34)
 a.table_address('t0');a.i(9,'t1','zero',SLOTS)
 a.label('get_find');a.i(35,'t2','t0',0);a.branch(4,'t2','v0','get_compare')
 a.i(9,'t0','t0',STRIDE);a.i(9,'t1','t1',-1);a.branch(5,'t1','zero','get_find');a.ret()
 a.label('get_compare');a.i(9,'t3','t0',4);a.move('t4','v0');a.i(9,'t5','zero',9)
 a.label('get_cell');a.i(37,'t6','t3',0);a.i(37,'t7','t4',0)
 a.branch(5,'t6','t7','get_fallback');a.branch(4,'t6','zero','get_full')
 a.i(9,'t3','t3',2);a.i(9,'t4','t4',2);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','get_cell')
 a.label('get_full');a.i(9,'v0','t0',4)
 a.label('get_fallback');a.ret()
def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 hooks={0x57578:('copy_name',3<<26|0x1e4b20>>2),0x57530:('get_name',0x00052940)}
 out,r=append(old,emit,hooks,bytes(SLOTS*STRIDE));out=bytearray(out)
 # Getter entry is a tail jump; preserve its incoming return address.
 w=struct.unpack_from('<I',out,192+0x57530)[0];struct.pack_into('<I',out,192+0x57530,w-(1<<26))
 assert struct.unpack_from('<I',old,192+0x57534)[0]==0x00851021
 struct.pack_into('<I',out,192+0x57534,0)
 # The old seven-cell padding loop would trim an interior space in a prefix.
 assert struct.unpack_from('<I',old,192+0x57580)[0]==0x2625000e
 struct.pack_into('<I',out,192+0x57580,0x1000000e)
 out=bytes(out);seg=parse_elf(out)['phdrs'][3];assert seg[6]&2
 r.update(source_sha256=sha(old),output_sha256=sha(out),slots=SLOTS,display_bytes_per_slot=CAPACITY,native_cache_bytes=20,native_prefix_cells=9,save_layout_unchanged=True,numeric_fields_unchanged=True,structure=validate_loader_structure(out))
 return out,r
def prepare_names(source):return {3:source.resource('02.DAT',3)},[]
if __name__=='__main__':
 import json
 _,r=prepare_elf();print(json.dumps(dict(mode='preview',helper=r['code_address'],slots=SLOTS,full_name_bytes=CAPACITY,native_name_bytes=20,hooks=r['hooks']),indent=2))
