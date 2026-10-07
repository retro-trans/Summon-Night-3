"""Read-only execution through 067 and retained 066 Give Food handlers."""
import json,struct
from status_fix_067 import ROOT,prepare_elf
from verify_menu_vwf_020 import CPU
from dialogue_encoding import encode_dialogue
from font_patch import CODE_VA
def verify():
 elf,r=prepare_elf();metrics=json.loads((ROOT/'work/ui/latin_font_metrics.json').read_text())['characters'];rows=[]
 text='ЕЁSwitch Й Give Food';raw=encode_dialogue(text,'ЕЁЙ')[0]+b'\0\0';index=text.index('Й')
 width=sum(metrics[c]['proposed_advance_pixels']*.875 if c in metrics else 13 for c in text[:index])
 for base in (0x08804000,0x0890c000):
  c=CPU(elf,r,base);ctx=0x09000000;desc=0x09002000;cb=base+0x1000
  c.store(ctx,bytes(0x200));c.store(ctx+0x4c+58,raw);c.store(desc,bytes(0x110));c.store(desc+0x100,bytes([index,1]));c.set('sp',0x09f00000);c.set('s2',ctx);c.set('s3',desc);c.set('a0',desc);c.set('a2',cb)
  c.fp[12]=int.from_bytes(struct.pack('<f',118+13*index),'little');seen=[]
  def callback(m):seen.append(struct.unpack('<f',struct.pack('<I',m.fp[12]))[0]);return {}
  c.native_handlers={cb:callback};c.run(int(r['code_address'],16)-CODE_VA+r['labels']['skills_icon'])
  assert seen==[118+width],seen;assert c.reg[29]==0x09f00000
  rows.append(dict(base=hex(base),x=seen[0],stack_restored=True))
 return dict(passed=True,actual_retained_food_handler=True,cases=rows)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
