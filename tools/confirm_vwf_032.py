"""Proportional centered glyphs for the Start Battle confirmation bundle."""
import json,struct,hashlib
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
from stages_pupil_names import parse_elf
import notice_vwf_027 as notice
BASE=ROOT/'work/output/0.1.31'
ROWS=[(0x32e9c0,'Start battle?'),(0x32e9dc,'Yes'),(0x32e9e4,'No')]

def prepare_elf():
 data=(BASE/'EBOOT.elf').read_bytes();ph=parse_elf(data)['phdrs'];entries=[];values=[]
 from dialogue_encoding import encode_dialogue
 oldtext=notice.TEXT
 try:
  for address,text in ROWS:
   offset=next(p[1]+address-p[2] for p in ph if p[0]==1 and p[2]<=address<p[2]+p[4])
   raw=encode_dialogue(text,'')[0]+b'\0\0';assert data[offset:offset+len(raw)]==raw
   notice.TEXT=text;v,w=notice.positions()
   entries.append(dict(address=address,text=text,table_offset=len(values)*4,positions=v,width=w*.875));values+=v
 finally:notice.TEXT=oldtext
 hookword=struct.unpack_from('<I',data,notice.HOOK+192)[0];assert hookword>>26==3
 fallback=(hookword&0x3ffffff)<<2
 def emit(a):
  a.label('position');a.i(35,'t0','s7',0)
  for n,e in enumerate(entries):
   address=e['address'];a.relocs.append((len(a.words)*4,0x305));a.i(15,'t1','zero',(address+0x8000)>>16)
   a.relocs.append((len(a.words)*4,0x306));a.i(9,'t1','t1',address&65535)
   a.branch(5,'t0','t1',f'next{n}');a.i(11,'t1','s1',len(e['text']));a.branch(4,'t1','zero','fallback')
   a.table_address('t0');a.i(9,'t0','t0',e['table_offset']);a.branch(4,'zero','zero','adjust');a.label(f'next{n}')
  a.branch(4,'zero','zero','fallback');a.label('adjust')
  a.emit(REG['s1']<<16|REG['t1']<<11|2<<6);a.emit(REG['t0']<<21|REG['t1']<<16|REG['t0']<<11|0x21)
  a.fp_mem(49,2,0,'t0');a.fp_mem(49,4,0x10,'sp')
  def mul(rd,rs,rt):a.emit(17<<26|16<<21|rt<<16|rs<<11|rd<<6|2)
  mul(2,2,4);a.fp_mem(49,4,0x30,'sp');mul(2,2,4)
  a.fp_mem(49,4,8,'s7');a.i(15,'t0','zero',0x3f00);a.emit(17<<26|4<<21|REG['t0']<<16|6<<11);mul(4,4,6)
  a.add_float(12,12,2);a.add_float(12,12,4)
  a.label('fallback');a.jump(fallback,link=False)
 data,r=append(data,emit,{notice.HOOK:('position',hookword)},struct.pack('<%df'%len(values),*values))
 r.update(rows=entries,fallback=hex(fallback))
 return data,dict(entries=[],skipped=[],notice_vwf=r,patched_elf_sha256=hashlib.sha256(data).hexdigest())
def prepare_tables(source):return {},{},source.resource('00.DAT',44),dict(units=[],tables=[])
