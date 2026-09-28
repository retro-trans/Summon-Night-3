"""Center the existing tutorial notice with measured proportional glyph positions."""
import json,struct
from sn3_archive import ROOT
from menu_code_020 import append
from font_patch import REG

TEXT='Tutorials: see Gallery.'
NOTICE=0x34a038
HOOK=0x1b670

def positions():
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 offsets=[];advance=0
 for c in TEXT:
  m=metrics[c];b=m['ink_bounds_inclusive'];left=b[0] if b else 0;width=b[2]-b[0]+1 if b else 0
  offsets.append(advance-left);ink_end=advance+width;advance+=m['proposed_advance_pixels']
 return [x-ink_end/2-i*16 for i,x in enumerate(offsets)],ink_end

def emit(a):
 a.label('notice_position');a.i(35,'t0','s7',0)
 a.relocs.append((len(a.words)*4,0x305));a.i(15,'t1','zero',(NOTICE+0x8000)>>16)
 a.relocs.append((len(a.words)*4,0x306));a.i(9,'t1','t1',NOTICE&65535)
 a.branch(5,'t0','t1','native');a.i(11,'t0','s1',len(TEXT));a.branch(4,'t0','zero','native')
 a.table_address('t0');a.emit(REG['s1']<<16|REG['t1']<<11|2<<6)
 a.emit(REG['t0']<<21|REG['t1']<<16|REG['t0']<<11|0x21)
 a.fp_mem(49,2,0,'t0');a.fp_mem(49,4,0x10,'sp')
 def mul(rd,rs,rt):a.emit(17<<26|16<<21|rt<<16|rs<<11|rd<<6|2)
 mul(2,2,4);a.fp_mem(49,4,0x30,'sp');mul(2,2,4)
 a.fp_mem(49,4,8,'s7');a.i(15,'t0','zero',0x3f00);a.emit(17<<26|4<<21|REG['t0']<<16|6<<11);mul(4,4,6)
 a.add_float(12,12,2);a.add_float(12,12,4)
 a.label('native');a.emit(REG['a2']<<21|8);a.emit(0)

def prepare(data):
 values,width=positions();out,r=append(data,emit,{HOOK:('notice_position',REG['a2']<<21|REG['ra']<<11|9)},struct.pack('<%df'%len(values),*values))
 r.update(profile='tutorial_notice_proportional_positions',text=TEXT,source_address=hex(NOTICE),native_glyph_scale=.875,ink_width_pixels=width*.875,scope='Only the existing tutorial-notice text pointer; all other messages use native placement.')
 return out,r
