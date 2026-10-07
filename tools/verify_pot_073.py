"""Run default-name, rename and saved-name/metadata regression checks."""
import json,struct
import verify_pot_072 as previous
from pot_fix_073 import prepare_elf
from verify_guards_057 import GuardCPU
from dialogue_encoding import encode_dialogue
from verify_pot_071 import run
def verify():
 elf,r=prepare_elf();previous.prepare_elf=prepare_elf;result=previous.verify();cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base)
  # Execute the actual native load fragment with its newly relocated calls.
  lo,hi=0x6299c,0x629cc;data=bytearray(elf[192+lo:192+hi])
  for p in range(0,len(data),4):
   w=struct.unpack_from('<I',data,p)[0]
   if w>>26 in (2,3):struct.pack_into('<I',data,p,w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff)
  m.store(base+lo,data);target=0x09400c34;src=0x09800000
  for binding in list(range(121))+[121,122,255,256,0x8582,0xffff]:
   for text in ('Summon Mate','Custom'):
    raw=encode_dialogue(text,'')[0]+b'\0\0';m.store(src,raw[:20].ljust(20,b'\0')+struct.pack('<HHB',3,binding,0x82))
    m.store(target,bytes(32));m.r=[0]*32;m.r[29]=0x09f00000;m.r[31]=0x08801234
    m.r[16]=target-0xc34;m.r[20]=src-0x6924;m.r[21]=src-0x6924
    m.r[30]=src-0x6924;m.r[23]=target;m.r[22]=src;pc=base+lo
    for _ in range(1000):
     if pc==base+hi:break
     pc=m.step(pc)
    else:raise AssertionError('Load fragment instruction budget')
    assert m.bytes(target+18,2)==bytes(2)
    actual=struct.unpack('<HH',m.bytes(target+20,4))
    assert actual==((binding,0x82) if binding<121 else (0,0)),(binding,actual)
    assert m.r[4]==0 and m.r[29]==0x09f00000
    assert m.bytes(src,min(20,len(raw)))==raw[:20]
    cases+=1
 result.update(saved_record_cases=cases,valid_bindings_preserved=True,invalid_bindings_cleared=True,saved_name_copy_terminated=True)
 return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
