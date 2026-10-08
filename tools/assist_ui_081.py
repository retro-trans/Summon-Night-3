"""Proportional Assist INFO labels and matching help-button coordinates."""
import hashlib,json,struct
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import parse_elf,validate_loader_structure
from dialogue_encoding import encode_dialogue

BASE=ROOT/'work/output/0.1.80'
FIELDS=(0x73b1c,0x73cbc)

def emit(a,prior):
 def add(rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x21)
 def sub(rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x23)
 def shift(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
 # Match the staged Assist-only prefix, independent of the power/range row
 # preceding it. The native icon index is twelve and rows have 29 U16 cells.
 a.label('assist_icon')
 a.i(36,'t0','s3',0x101);a.i(11,'t1','t0',3);a.branch(4,'t1','zero','assist_fallback')
 a.i(36,'t1','s3',0x100);a.i(9,'t2','zero',12);a.branch(5,'t1','t2','assist_fallback')
 shift('t1','t0',5);sub('t1','t1','t0');sub('t1','t1','t0');sub('t1','t1','t0');shift('t1','t1',1)
 add('t0','s2','t1');a.i(9,'t0','t0',0x4c);a.table_address('t1');a.i(9,'t2','zero',12)
 a.label('compare');a.i(37,'t3','t0',0);a.i(37,'t4','t1',0);a.branch(5,'t3','t4','assist_fallback')
 a.i(9,'t0','t0',2);a.i(9,'t1','t1',2);a.i(9,'t2','t2',-1);a.branch(5,'t2','zero','compare')
 a.i(9,'sp','sp',-64)
 for reg,o in [('ra',60),('a0',48),('a2',52),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(43,reg,'sp',o)
 a.i(9,'s0','t0',-24);a.i(9,'s1','zero',12);a.move('s2','zero')
 a.label('sum');a.i(37,'a0','s0',0);a.jump(0x32e380)
 a.i(9,'t3','zero',16);a.branch(4,'a0','t3','unknown');shift('t3','v0',3);sub('t3','t3','v0');a.branch(4,'zero','zero','add')
 a.label('unknown');a.i(9,'t3','zero',104)
 a.label('add');add('s2','s2','t3');a.i(9,'s0','s0',2);a.i(9,'s1','s1',-1);a.branch(5,'s1','zero','sum')
 a.i(9,'s2','s2',-12*104);a.int_to_float('s2',4);a.i(15,'t3','zero',0x3e00);a.emit(17<<26|4<<21|REG['t3']<<16|2<<11)
 a.emit(17<<26|16<<21|2<<16|4<<11|4<<6|2);a.add_float(12,12,4)
 a.i(35,'a0','sp',48);a.i(35,'t9','sp',52);a.emit(REG['t9']<<21|REG['ra']<<11|9);a.emit(0)
 for reg,o in [('ra',60),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(35,reg,'sp',o)
 a.i(9,'sp','sp',64);a.ret()
 a.label('assist_fallback');a.jump(prior,link=False)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old)
 word=struct.unpack_from('<I',old,0x64490+192)[0];assert word>>26==3
 prior=(word&0x3ffffff)<<2
 r= parse_elf(old)['phdrs'][2];relocs=set(struct.iter_unpack('<II',old[r[1]:r[1]+r[4]]))
 for site in FIELDS:
  assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbdec>>2
  assert struct.unpack_from('<I',old,site+196)[0]==0x34060001 and (site,4) in relocs
  struct.pack_into('<I',out,site+192,3<<26|0x347b5c>>2)
 result,report=append(bytes(out),lambda a:emit(a,prior),{0x64490:('assist_icon',word)},encode_dialogue('Assist only ','')[0]+bytes(4))
 assert validate_loader_structure(result)
 report.update(version='0.1.81',baseline_sha256=hashlib.sha256(old).hexdigest(),output_sha256=hashlib.sha256(result).hexdigest(),fallback=prior,fields=[hex(s) for s in FIELDS],scope='Assist-only help icons and required-participant INFO labels, including default, custom and category names. Saved names and combat logic unchanged.')
 return result,report
