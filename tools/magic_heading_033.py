"""Use saved-name translation and VWF when updating the battle magic heading."""
import struct,hashlib
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
BASE=ROOT/'work/output/0.1.32'
HOOK=0xc0814
LIST=0x34a0c8

def emit(a):
 a.label('heading');a.branch(4,'a1','zero','native');a.i(35,'t0','a0',0xc0);a.branch(4,'t0','zero','native')
 # The established list renderer translates only exact default-name matches,
 # preserves custom names, and selects a bounded native cache strip.
 a.i(9,'a2','zero',1);a.jump(LIST,link=False)
 a.label('native');a.jump(0x1cbee0,link=False)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 data,r=append(old,emit,{HOOK:('heading',3<<26|0x1cbee0>>2)})
 r.update(profile='battle_magic_heading_saved_name_vwf',call=hex(HOOK),existing_name_list=hex(LIST),save_files_unchanged=True)
 return data,dict(entries=[],skipped=[],heading=r,patched_elf_sha256=hashlib.sha256(data).hexdigest())
def prepare_tables(source):return {},{},source.resource('00.DAT',44),dict(units=[],tables=[])
