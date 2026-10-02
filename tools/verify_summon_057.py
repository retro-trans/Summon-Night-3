"""Execute the current hint wrapper at two load bases and check screen bounds."""
import argparse,json,struct
from pathlib import Path
from sn3_archive import ROOT
from stages_pupil_names import parse_elf
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from dialogue_encoding import encode_dialogue

def verify(elf):
 parsed=parse_elf(elf);p=parsed['phdrs'][3];r=parsed['phdrs'][2]
 records=list(struct.iter_unpack('<II',elf[r[1]:r[1]+r[4]]))
 offset=p[1]+0x33fd5c-p[2]
 assert elf[offset:offset+10]==encode_dialogue('Cast','')[0]+b'\0\0','Loaded hint still contains old text'
 report=dict(added_segment_file_offset=p[1],added_segment_bytes=p[4],
  extra_relocation_records=[x for x in records if x[1]>>8&255==3])
 wrapper=(struct.unpack_from('<I',elf,0x1549f8+0xc0)[0]&0x3ffffff)<<2
 assert wrapper==0x347b5c
 labels={0x154aa8:'Confirm',0x154b44:'Set Name',0x154c1c:'Cast',0x154c84:'Dismiss'}
 for va in labels:
  assert struct.unpack_from('<I',elf,va+0xc0)[0]==3<<26|wrapper>>2
  assert (va,4) in records,('missing jump relocation',hex(va))
 cases=0
 for base in (0x08804000,0x0890c000):
  for text in list(labels.values())+['A'*17]:
   c=CPU(elf,report,base);c.store(0x09effe00,b'\x79'*1024);c.set('sp',0x09f00000)
   for register in range(16,31):c.reg[register]=0x34560000+register
   before=c.reg[16:31].copy();obj=0x09000000;src=0x09010000;count=len(text)
   c.store(src,encode_dialogue(text,'')[0]+b'\0\0')
   for name,value in [('a0',obj),('a1',src),('a2',1)]:c.set(name,value)
   calls=[]
   def length(m):assert m.reg[4]==src;return {'v0':count}
   def bind(m):assert m.reg[4:8]==[obj,src,count,1];calls.append('vwf');return {'v0':123}
   def fallback(m):assert m.reg[4:7]==[obj,src,1];calls.append('native');return {'v0':456}
   c.native_handlers={base+0x1e4ac8:length,base+0x32e060:bind,base+0x1cbdec:fallback}
   c.run(wrapper-CODE_VA)
   assert calls==['vwf' if count<=16 else 'native']
   assert c.reg[16:24]+c.reg[26:31]==before[:8]+before[10:]
   assert c.bytes(0x09effe00,0x1a0)==b'\x79'*0x1a0 and c.bytes(0x09f00000,0x200)==b'\x79'*0x200
   cases+=1
 metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters']
 rows=[]
 for text,start,limit in [('Type',420,480),('Confirm',386,480),('Set Name',391,480),('Cast',330,388),('Dismiss',404,480)]:
  # Include the wrapper's three-pixel ink inset and the full final glyph width.
  width=3+sum(metrics[ch]['proposed_advance_pixels'] for ch in text)
  assert start+width<=limit,(text,start,width,limit)
  rows.append(dict(text=text,start=start,widest_end=start+width,limit=limit))
 assert 367+len('Cast Magic')*16>431 # Reported old overlap is detected.
 return dict(passed=True,actual_mips_cases=cases,load_bases=2,stack_guards=True,
  existing_wrapper_reused=True,all_caller_jump_relocations_present=True,layout=rows,
  limits=['Native graphics calls are stubbed; in-game screenshots are checked separately.'])

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build',default='work/output/0.1.57');p.add_argument('--report');a=p.parse_args()
 r=verify((ROOT/a.build/'EBOOT.elf').read_bytes());print(json.dumps(r,indent=2))
 if a.report:(ROOT/a.report).write_text(json.dumps(r,indent=2)+'\n')
