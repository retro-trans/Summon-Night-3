"""Bound shared help staging and native glyph lookup; immutable v0.1.48 input."""
import hashlib,struct
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va

BASE=ROOT/'work/output/0.1.48'
HELP_SITE=0x64820
GLYPH_SITE=0x1d8f58

def prepare_elf():
 old=(BASE/'EBOOT.elf').read_bytes()
 marker=encode_dialogue('Text error','')[0]+b'\0\0\0\0'
 table=bytes(16)+marker;table+=bytes(-len(table)%4)
 def emit(a):
  def sltu(rd,rs,rt):a.emit(REG[rs]<<21|REG[rt]<<16|REG[rd]<<11|0x2b)
  a.label('help_guard')
  # Entry is a J, not JAL. Preserve ra, all callee-saved registers and the
  # six incoming arguments a0..a3/t0/t1. Only t2..t9 are scratch.
  a.branch(4,'a1','zero','help_ok')
  a.move('t2','a1');a.i(9,'t3','zero',0);a.i(9,'t4','zero',0);a.i(9,'t5','zero',0)
  a.i(12,'t6','a1',1);a.branch(5,'t6','zero','bad_pointer')
  a.i(15,'t7','zero',0x0880);sltu('t6','a1','t7');a.branch(5,'t6','zero','bad_pointer')
  a.i(15,'t7','zero',0x0a00)
  a.label('scan_help');sltu('t6','t2','t7');a.branch(4,'t6','zero','bad_pointer')
  a.i(37,'t6','t2',0);a.i(9,'t2','t2',2)
  a.branch(4,'t6','zero','end_line')
  a.i(9,'t3','t3',1);a.i(9,'t4','t4',1)
  a.i(11,'t6','t3',28);a.branch(4,'t6','zero','too_long')
  a.i(11,'t6','t4',55);a.branch(4,'t6','zero','too_long')
  a.branch(4,'zero','zero','scan_help')
  a.label('end_line');a.branch(4,'t3','zero','help_ok')
  a.i(9,'t5','t5',1);a.i(9,'t3','zero',0);a.i(11,'t6','t5',3)
  a.branch(5,'t6','zero','scan_help')
  a.branch(4,'zero','zero','help_ok')
  a.label('bad_pointer');a.i(9,'t8','zero',2);a.branch(4,'zero','zero','reject_help')
  a.label('too_long');a.i(9,'t8','zero',1)
  a.label('reject_help');a.table_address('t9');a.i(35,'t6','t9',0);a.i(9,'t6','t6',1)
  a.i(43,'t6','t9',0);a.i(43,'t8','t9',8);a.i(43,'a1','t9',12);a.i(9,'a1','t9',16)
  a.label('help_ok');a.i(9,'sp','sp',-0x90);a.jump(0x64828,link=False)

  a.label('glyph_guard')
  # Native routine has already saved ra. Do not change live a0 except on
  # invalid input. Validate both CP932 bytes before indexing its font map.
  a.i(12,'a1','a0',255)
  a.i(11,'t0','a1',0x81);a.branch(5,'t0','zero','bad_glyph')
  a.i(11,'t0','a1',0xa0);a.branch(5,'t0','zero','check_trail')
  a.i(11,'t0','a1',0xe0);a.branch(5,'t0','zero','bad_glyph')
  a.i(11,'t0','a1',0xfd);a.branch(4,'t0','zero','bad_glyph')
  a.label('check_trail');a.emit(REG['a0']<<16|REG['t0']<<11|8<<6|2)
  a.i(11,'t1','t0',0x40);a.branch(5,'t1','zero','bad_glyph')
  a.i(11,'t1','t0',0xfd);a.branch(4,'t1','zero','bad_glyph')
  a.i(9,'t1','zero',0x7f);a.branch(5,'t0','t1','glyph_ok')
  a.label('bad_glyph');a.table_address('t0');a.i(35,'t1','t0',4);a.i(9,'t1','t1',1)
  a.i(43,'t1','t0',4);a.i(9,'t1','zero',3);a.i(43,'t1','t0',8);a.i(43,'a0','t0',12)
  a.i(13,'a0','zero',0x4881);a.i(41,'a0','s2',0)
  a.label('glyph_ok');a.i(12,'a1','a0',255);a.i(9,'a1','a1',-0x80)
  a.jump(0x1d8f60,link=False)
 data,report=append(old,emit,{HELP_SITE:('help_guard',0x27bdff70),GLYPH_SITE:('glyph_guard',0x308500ff)},table)
 out=bytearray(data);word=struct.unpack_from('<I',out,HELP_SITE+192)[0]
 struct.pack_into('<I',out,HELP_SITE+192,(word&0x03ffffff)|(2<<26))
 report['diagnostic_address']=hex(int(report['code_address'],16)+report['labels']['table'])
 report['diagnostic_fields']=['help_rejections','invalid_glyphs','last_reason','last_value']
 report['help_limits']=dict(rows=3,cells_per_row=27,total_glyphs=54,source_address_min='0x08800000',source_address_end='0x0a000000')
 report['entries']=[];report['help_entry_preserves_ra']=True
 report['patched_elf_sha256']=hashlib.sha256(out).hexdigest()
 return bytes(out),report

def prepare_tables(source):
 return {3:source.resource('02.DAT',3)},{},source.resource('00.DAT',44),dict(units=[],tables=[])

def verify(elf,static):
 from verify_guards_049 import verify as run
 return run(elf,static)
