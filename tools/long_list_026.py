"""Pack 17–32 Latin cells into an existing 16-cell native cache strip.

The native allocator has only 1-, 8- and 16-cell entries. Populate it twice,
save both untouched glyph chunks on the stack, then pack their ink back into
the same 256-pixel strip. Only measured labels fitting that strip qualify.
"""
import json,struct
from font_patch import REG
from menu_code_020 import append
from sn3_archive import ROOT

OLD_LIST=0x348a28
SAVED_NAME=0x3489b8
LOOKUP=0x347fe8

def emit(a):
 def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
 def shift(rd,rt,n,right=False):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6|(2 if right else 0))
 def address(reg,va):
  a.relocs.append((len(a.words)*4,0x305));a.i(15,reg,'zero',(va+0x8000)>>16)
  a.relocs.append((len(a.words)*4,0x306));a.i(9,reg,reg,va&65535)
 a.label('list');a.i(9,'sp','sp',-48)
 for reg,off in [('ra',44),('a0',16),('a1',20),('a2',24)]:a.i(43,reg,'sp',off)
 a.move('a0','a1');a.jump(SAVED_NAME);a.i(43,'v0','sp',28)
 a.move('a0','v0');a.jump(0x1e4ac8);a.i(43,'v0','sp',32)
 a.i(11,'t0','v0',17);a.branch(5,'t0','zero','old')
 a.i(11,'t0','v0',33);a.branch(4,'t0','zero','old')
 a.i(35,'a2','sp',28);a.move('a3','v0');a.move('t8','zero')
 a.label('measure');a.i(37,'a0','a2',0);a.jump(LOOKUP)
 # Unknown glyphs keep the original path; this helper packs Latin only.
 a.i(9,'t3','zero',16);a.branch(4,'a0','t3','old')
 r(0x21,'t8','t8','v0');a.i(9,'a2','a2',2);a.i(9,'a3','a3',-1);a.branch(5,'a3','zero','measure')
 a.i(11,'t0','t8',257);a.branch(4,'t0','zero','old')
 a.i(35,'a0','sp',16);a.i(35,'a1','sp',28);a.i(35,'a2','sp',32);a.i(35,'a3','sp',24)
 a.jump('long_bind');a.branch(4,'zero','zero','return')
 a.label('old');a.i(35,'a0','sp',16);a.i(35,'a1','sp',20);a.i(35,'a2','sp',24);a.jump(OLD_LIST)
 a.label('return');a.i(35,'ra','sp',44);a.i(9,'sp','sp',48);a.ret()

 a.label('long_bind');a.i(9,'sp','sp',-4288)
 saved=[(reg,4224+i*4) for i,reg in enumerate(['s0','s1','s2','s3','s4','s5','s6','s7','fp','ra'])]
 for reg,off in saved:a.i(43,reg,'sp',off)
 a.move('s0','a0');a.move('s2','a1');a.move('s3','a2')
 a.i(43,'s2','sp',4128);a.i(43,'s3','sp',4132)
 a.i(9,'a2','zero',16);a.jump(0x1cbe48);a.i(43,'v0','sp',4268)
 a.i(35,'s1','s0',0xc0);a.branch(4,'s1','zero','done')
 address('t0',0x22a340);a.i(35,'s4','t0',0);a.i(9,'s4','s4',0xcac)
 a.i(35,'t0','s0',0);a.i(13,'t0','t0',0x100);a.i(43,'t0','s0',0)
 a.i(37,'s6','s4',4);shift('s6','s6',1,True)
 a.i(35,'s5','s4',0x28);a.i(37,'t0','s1',2)
 r(0x18,'zero','t0','s6');a.emit(REG['t0']<<11|0x12);r(0x21,'s5','s5','t0')
 a.i(37,'t0','s1',0);shift('t0','t0',1,True);r(0x21,'s5','s5','t0')
 shift('s7','s3',3);a.move('fp','zero')
 a.label('chunk')
 a.move('a0','s4');a.move('a1','s1');shift('t0','fp',1);r(0x21,'a2','s2','t0')
 r(0x23,'a3','s3','fp');a.i(11,'t0','a3',17);a.branch(5,'t0','zero','count_ready');a.i(9,'a3','zero',16)
 a.label('count_ready');a.i(43,'a3','sp',4160);a.jump(0x1d8e34)
 a.move('t0','s5');shift('t1','fp',3);r(0x21,'t1','sp','t1');a.i(9,'t2','zero',16)
 a.i(35,'t7','sp',4160);shift('t7','t7',3)
 a.label('copy_row');a.move('t3','t0');a.move('t4','t1');a.move('t5','t7')
 a.label('copy_byte');a.i(36,'t6','t3',0);a.i(40,'t6','t4',0)
 a.i(9,'t3','t3',1);a.i(9,'t4','t4',1);a.i(9,'t5','t5',-1);a.branch(5,'t5','zero','copy_byte')
 r(0x21,'t0','t0','s6');r(0x21,'t1','t1','s7');a.i(9,'t2','t2',-1);a.branch(5,'t2','zero','copy_row')
 a.i(35,'t0','sp',4160);r(0x21,'fp','fp','t0');a.branch(5,'fp','s3','chunk')
 # Invalidate all 16 cached codes after the last population, not before.
 a.i(37,'t0','s1',2);shift('t0','t0',4,True);a.i(37,'t1','s4',8)
 r(0x18,'zero','t0','t1');a.emit(REG['t0']<<11|0x12)
 a.i(37,'t1','s1',0);shift('t1','t1',4,True);r(0x21,'t0','t0','t1');shift('t0','t0',1)
 a.i(35,'t1','s4',0x24);r(0x21,'t0','t0','t1');a.i(9,'t1','zero',16)
 a.label('invalidate');a.i(41,'zero','t0',0);a.i(9,'t0','t0',2);a.i(9,'t1','t1',-1);a.branch(5,'t1','zero','invalidate')
 a.move('t0','s5');a.i(9,'t1','zero',16)
 a.label('clear_row');a.move('t2','t0');a.i(9,'t3','zero',128)
 a.label('clear_byte');a.i(40,'zero','t2',0);a.i(9,'t2','t2',1);a.i(9,'t3','t3',-1);a.branch(5,'t3','zero','clear_byte')
 r(0x21,'t0','t0','s6');a.i(9,'t1','t1',-1);a.branch(5,'t1','zero','clear_row')
 a.move('s0','zero');a.move('s1','zero')
 a.label('character');a.i(35,'t0','sp',4128);shift('t1','s0',1);r(0x21,'t0','t0','t1');a.i(37,'a0','t0',0);a.jump(LOOKUP)
 a.i(43,'v0','sp',4136);a.move('s2','a0');a.move('s3','v1');a.branch(4,'s2','zero','next_character')
 shift('s4','s0',3);r(0x21,'s4','sp','s4');a.move('fp','s5');a.i(9,'t9','zero',16)
 a.label('pixel_row');a.move('t0','zero')
 a.label('pixel');r(0x21,'t1','s3','t0');shift('t2','t1',1,True);r(0x21,'t2','s4','t2');a.i(36,'t3','t2',0)
 a.i(12,'t1','t1',1);shift('t1','t1',2);r(6,'t3','t1','t3');a.i(12,'t3','t3',15)
 r(0x21,'t1','s1','t0');shift('t2','t1',1,True);r(0x21,'t2','fp','t2');a.i(12,'t1','t1',1);shift('t1','t1',2);r(4,'t3','t1','t3')
 a.i(36,'t4','t2',0);r(0x25,'t3','t3','t4');a.i(40,'t3','t2',0);a.i(9,'t0','t0',1);a.branch(5,'t0','s2','pixel')
 r(0x21,'s4','s4','s7');r(0x21,'fp','fp','s6');a.i(9,'t9','t9',-1);a.branch(5,'t9','zero','pixel_row')
 a.label('next_character');a.i(35,'t0','sp',4136);r(0x21,'s1','s1','t0');a.i(9,'s0','s0',1);a.i(35,'t0','sp',4132);a.branch(5,'s0','t0','character')
 a.label('done');a.i(35,'v0','sp',4268)
 for reg,off in saved:a.i(35,reg,'sp',off)
 a.i(9,'sp','sp',4288);a.ret()

def prepare(data):
 out,r=append(data,emit,{p:('list',3<<26|OLD_LIST>>2) for p in (0x1b390,0x14ecf8)})
 r.update(profile='long_latin_labels_in_native_16_cell_cache',max_input_cells=32,cache_cells=16,max_advance_pixels=256)
 return out,r
