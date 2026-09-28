"""Execute the emitted long-label helper against real glyphs and 16-cell guards."""
import json,struct
from long_list_026 import prepare
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from font_metrics import collect
from sn3_archive import ROOT

def verify():
 data,r=prepare((ROOT/'work/output/0.1.25/EBOOT.elf').read_bytes())
 metrics,font=collect();chars=metrics['characters'];cases=0
 for base in (0x08804000,0x0890c000):
  for sample in ["Crush! Light Gen. Sword","Crush! Light Gen.'s Sword",'i'*17,'i'*32,'A mixed long label',' '*25]:
   text=b''.join(bytes.fromhex(chars[c]['cp932_hex']) for c in sample)
   glyphs=[font[chars[c]['font_byte_offset']:chars[c]['font_byte_offset']+128] for c in sample]
   cpu=CPU(data,r,base);stack=0x09f00000;obj=0x09000000;entry=obj+0x1000;src=obj+0x2000
   manager=0x09100000;wrapper=manager+0xcac;bitmap=0x09200000;cache=0x09300000
   cpu.store(stack-4600,b'\x79'*4800);cpu.store(obj,bytes(0xe0));cpu.store(src,text+b'\0\0')
   cpu.store(entry,struct.pack('<4H',256,16,16,1));cpu.store(base+0x22a340,struct.pack('<I',manager))
   cpu.store(wrapper,bytes(64));cpu.store(wrapper+4,struct.pack('<H',512));cpu.store(wrapper+8,struct.pack('<H',32))
   cpu.store(wrapper+0x24,struct.pack('<II',cache,bitmap));cpu.store(cache,b'\xaa'*2048)
   initial=b'\xb6'*(256*64);cpu.store(bitmap,initial);calls=[]
   def bind(m):
    assert m.reg[4:8]==[obj,src,16,1]
    m.store(obj+0xc0,struct.pack('<I',entry));m.store(obj+0xcc,struct.pack('<II',16,16));return {'v0':0x12345}
   def populate(m):
    start=(m.reg[6]-src)//2;n=m.reg[7];assert m.reg[4:6]==[wrapper,entry] and 0<n<=16
    calls.append((start,n))
    for j,glyph in enumerate(glyphs[start:start+n]):
     for y in range(16):m.store(bitmap+(16+y)*256+128+j*8,glyph[y*8:y*8+8])
    m.store(cache+96,text[start*2:(start+n)*2]);return {}
   cpu.native_handlers={base+0x1cbe48:bind,base+0x1d8e34:populate,base+0x1e4ac8:lambda m:{'v0':len(sample)}}
   for n in range(16,31):cpu.reg[n]=0x34560000+n
   cpu.set('sp',stack);saved=cpu.reg[16:31].copy()
   for reg,value in [('a0',obj),('a1',src),('a2',1)]:cpu.set(reg,value)
   cpu.run(int(r['code_address'],16)-CODE_VA+r['labels']['list'])
   assert calls==[(0,16),(16,len(sample)-16)]
   assert cpu.reg[16:24]+cpu.reg[26:31]==saved[:8]+saved[10:] and cpu.reg[2]==0x12345
   assert cpu.bytes(stack-4600,160)==b'\x79'*160 and cpu.bytes(stack,200)==b'\x79'*200
   assert cpu.bytes(cache+96,32)==bytes(32)
   assert cpu.read(obj+0xcc,4)==cpu.read(obj+0xd0,4)==16
   target=bytearray(initial)
   for y in range(16):target[(16+y)*256+128:(17+y)*256]=bytes(128)
   x=0
   for c,glyph in zip(sample,glyphs):
    m=chars[c];b=m['ink_bounds_inclusive'];left=b[0] if b else 0;width=b[2]-b[0]+1 if b else 0
    for y in range(16):
     for p in range(width):
      v=glyph[y*8+(left+p)//2]>>(4*((left+p)%2))&15
      target[(16+y)*256+128+(x+p)//2]|=v<<(4*((x+p)%2))
    x+=m['proposed_advance_pixels']
   assert x<=256 and cpu.bytes(bitmap,len(target))==target,sample
   cases+=1
 return dict(cases=cases,relocation_bases=2,coverage=['real glyph pixel equality','two native chunks at most 16 cells','adjacent texture guards','stack guards','cache code invalidation','callee saved registers','16-cell draw extent'])

if __name__=='__main__':print(json.dumps(verify(),indent=2))
