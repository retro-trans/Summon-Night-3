"""Scoped Deployment VWF fields, support chunks and shortcut icon positions."""
import json,struct,hashlib
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import parse_elf
BASE=ROOT/'work/output/0.1.28'
LOOKUP=0x32e380
PROMPT=0x338a2c
FIELDS={'name':0x16e9d4,'class':0x16ea58,'attack':0x16f8e8,'stance':0x16fa1c}

def emit(a):
 def r(fn,rd,rs,rt='zero'):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|fn)
 def shift(rd,rt,n):a.emit(REG[rt]<<16|REG[rd]<<11|n<<6)
 def save():
  a.i(9,'sp','sp',-64)
  for reg,off in [('ra',60),('a0',48),('a2',52),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(43,reg,'sp',off)
 def restore():
  for reg,off in [('ra',60),('s0',32),('s1',36),('s2',40),('s3',44)]:a.i(35,reg,'sp',off)
  a.i(9,'sp','sp',64);a.ret()
 def sum_prefix(label,unknown=104):
  a.move('s2','zero');a.label(label+'_loop');a.branch(4,'s1','zero',label+'_done')
  a.i(37,'a0','s0',0);a.jump(LOOKUP)
  a.i(9,'t3','zero',16);a.branch(4,'a0','t3',label+'_unknown')
  shift('t3','v0',3);r(0x23,'t3','t3','v0');a.branch(4,'zero','zero',label+'_add')
  a.label(label+'_unknown');a.i(9,'t3','zero',unknown)
  a.label(label+'_add');r(0x21,'s2','s2','t3');a.i(9,'s0','s0',2);a.i(9,'s1','s1',-1);a.branch(4,'zero','zero',label+'_loop')
  a.label(label+'_done')
 def scale_float(reg):
  a.int_to_float('s2',reg);a.i(15,'t3','zero',0x3e00);a.emit(17<<26|4<<21|REG['t3']<<16|2<<11)
  a.emit(17<<26|16<<21|2<<16|reg<<11|reg<<6|2)
 a.label('support_position');save();a.move('s0','s5');a.move('s1','s4')
 sum_prefix('support',112);scale_float(12);a.add_float(12,12,24)
 a.i(35,'a0','sp',48);a.jump(0x1e6140);restore()
 a.label('shortcut_icons')
 a.i(35,'t0','s2',0x44);a.branch(4,'t0','zero','native_icon')
 a.relocs.append((len(a.words)*4,0x305));a.i(15,'t1','zero',(PROMPT+0x8000)>>16)
 a.relocs.append((len(a.words)*4,0x306));a.i(9,'t1','t1',PROMPT&65535)
 a.label('prompt_compare');a.i(37,'t2','t0',0);a.i(37,'t3','t1',0)
 a.branch(5,'t2','t3','native_icon');a.branch(4,'t2','zero','prompt_match')
 a.i(9,'t0','t0',2);a.i(9,'t1','t1',2);a.branch(4,'zero','zero','prompt_compare')
 a.label('prompt_match')
 save();a.move('s0','s2');a.i(36,'t0','s3',0x101)
 # Source row has 29 U16 cells, including icon placeholders.
 shift('t1','t0',5);r(0x23,'t1','t1','t0');r(0x23,'t1','t1','t0');r(0x23,'t1','t1','t0');shift('t1','t1',1)
 r(0x21,'s0','s0','t1');a.i(9,'s0','s0',0x4c)
 a.i(36,'s1','s3',0x100);a.move('s3','s1');sum_prefix('icon')
 # f12 already includes native index*13. Replace that part only.
 shift('t0','s3',6);shift('t1','s3',5);r(0x21,'t0','t0','t1');shift('t1','s3',3);r(0x21,'t0','t0','t1');r(0x23,'s2','s2','t0')
 scale_float(4);a.add_float(12,12,4)
 a.i(35,'a0','sp',48);a.i(35,'t9','sp',52);a.emit(REG['t9']<<21|REG['ra']<<11|9);a.emit(0);restore()
 a.label('native_icon');a.emit(REG['a2']<<21|8);a.emit(0)

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes();out=bytearray(old);patches=[]
 rel=parse_elf(old)['phdrs'][2];rels=list(struct.iter_unpack('<II',old[rel[1]:rel[1]+rel[4]]))
 for name,site in FIELDS.items():
  assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbdec>>2
  assert struct.unpack_from('<I',old,site+196)[0]==0x34060001
  assert (site,4) in rels
  struct.pack_into('<I',out,site+192,3<<26|0x347b5c>>2);patches.append(dict(field=name,call=hex(site),wrapper='0x347b5c'))
 site=0x16eb94;assert struct.unpack_from('<I',old,site+192)[0]==3<<26|0x1cbe48>>2;assert (site,4) in rels
 struct.pack_into('<I',out,site+192,3<<26|0x32e060>>2)
 out,rpt=append(bytes(out),emit,{0x16ec0c:('support_position',3<<26|0x1e6140>>2),0x64490:('shortcut_icons',REG['a2']<<21|REG['ra']<<11|9)})
 return out,dict(entries=[],skipped=[],field_patches=patches,support_bind=hex(site),helpers=rpt,scope='Exact Deployment shortcut content, including runtime copies, only for icons; status field callers and support chunks only for VWF.',patched_elf_sha256=hashlib.sha256(out).hexdigest())

def prepare_tables(source):
 return {},{},source.resource('00.DAT',44),dict(units=[],tables=[])

if __name__=='__main__':print(json.dumps(prepare_elf()[1],indent=2))
