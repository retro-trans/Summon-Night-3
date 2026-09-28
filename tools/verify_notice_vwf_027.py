"""Execute the notice positioning hook at two load bases and verify its scope."""
import json,struct
from notice_vwf_027 import prepare,TEXT,NOTICE,positions
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from sn3_archive import ROOT

def verify():
 data,r=prepare((ROOT/'work/output/0.1.26/EBOOT.elf').read_bytes());values,width=positions();cases=0
 for base in [0x08804000,0x0890c000]:
  for match,index in [(True,i) for i in range(len(TEXT)+1)]+[(False,3)]:
   cpu=CPU(data,r,base);sp=0x09f00000;row=0x09000000;callback=base+0x1000;seen=[]
   cpu.store(sp,bytes(64));cpu.float_store(sp+0x10,.875);cpu.float_store(sp+0x30,1)
   cpu.store(row,struct.pack('<IIf',base+NOTICE if match else base+NOTICE+4,0,len(TEXT)*14))
   for i in range(16,31):cpu.reg[i]=0x55000000+i
   cpu.set('s1',index);cpu.set('s7',row);cpu.set('sp',sp);saved=cpu.reg[16:31].copy()
   cpu.set('a0',0x09001000);cpu.set('a2',callback)
   x=-len(TEXT)*7+index*14
   for reg,value in [(12,x),(13,1.25),(14,498)]:cpu.fp[reg]=struct.unpack('<I',struct.pack('<f',value))[0]
   def native(m):
    seen.append([struct.unpack('<f',struct.pack('<I',m.fp[n]))[0] for n in (12,13,14)])
    assert m.reg[4]==0x09001000;return {}
   cpu.native_handlers={callback:native}
   cpu.run(int(r['code_address'],16)-CODE_VA+r['labels']['notice_position'])
   expected=x+(values[index]*.875+len(TEXT)*7 if match and index<len(TEXT) else 0)
   assert len(seen)==1 and abs(seen[0][0]-expected)<.001 and seen[0][1:]==[1.25,498]
   assert cpu.reg[16:24]+cpu.reg[26:31]==saved[:8]+saved[10:]
   cases+=1
 return dict(cases=cases,load_bases=2,ink_width_pixels=width*.875,coverage=['all notice glyph positions','unrelated text unchanged','out-of-range index unchanged','Y/Z unchanged','native callback and preserved registers'])

if __name__=='__main__':print(json.dumps(verify(),indent=2))
