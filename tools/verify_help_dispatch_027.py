"""Execute both help dispatch paths, including relocated addresses."""
import json,struct
from help_dispatch_027 import prepare,VWF
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from sn3_archive import ROOT

def verify():
 data,r=prepare((ROOT/'work/output/0.1.26/EBOOT.elf').read_bytes());cases=0
 for base in [0x08804000,0x0890c000]:
  for mode,raw,native in [(6,b'\x83\xa3',True),(6,b'\x83\xa7',True),(6,b'\x82\x62',False),(6,b'\x83\x7e',False),(1,b'\x83\xa3',False),(6,b'\x83\xb6',True),(6,b'\x83\xb7',False)]:
   c=CPU(data,r,base);context=0x09000000;source=0x09000100;cb=base+0x1000;seen=[]
   c.store(context,bytes(128));c.store(context+0x34,struct.pack('<I',mode));c.store(context+0x4c,raw)
   c.set('s4',context);c.set('a2',cb)
   c.native_handlers={cb:lambda m:(seen.append('native') or {}),base+VWF:lambda m:(seen.append('vwf') or {})}
   c.run(int(r['code_address'],16)-CODE_VA+r['labels']['help_dispatch'])
   assert seen==['native' if native else 'vwf'],(mode,raw,seen)
   assert c.reg[20]==context
   cases+=1
 return dict(cases=cases,load_bases=2)
if __name__=='__main__':print(json.dumps(verify()))
