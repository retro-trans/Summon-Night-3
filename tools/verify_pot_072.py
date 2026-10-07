"""Execute actual default initialization, including its previously missed copy."""
import struct,json
import verify_pot_071 as previous
from pot_fix_072 import prepare_elf
from verify_guards_057 import GuardCPU
from dialogue_encoding import encode_dialogue

def verify():
 previous.prepare_elf=prepare_elf;result=previous.verify();elf,report=prepare_elf();cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,report,base);lo,hi=0x54850,0x54918
  data=bytearray(elf[192+lo:192+hi])
  for p in range(0,len(data),4):
   w=struct.unpack_from('<I',data,p)[0]
   if w>>26 in (2,3):struct.pack_into('<I',data,p,w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff)
  m.store(base+lo,data)
  getter=bytearray(elf[192+0x57530:192+0x57540])
  w=struct.unpack_from('<I',getter)[0];struct.pack_into('<I',getter,0,w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff)
  m.store(base+0x57530,getter);pool=0x09400000;src=0x09800000
  names=['Summon Mate','Stonework Base','Colossus Form','Shine Saber','R']
  m.r=[0]*32;m.r[4]=pool;m.r[29]=0x09f00000;m.r[31]=0x08801234
  pc=base+lo
  for _ in range(100000):
   if pc==base+hi:break
   if pc==base+0x1c2bc0:
    m.store(m.r[4],bytes([m.r[5]&255])*m.r[6]);pc=m.r[31]
   elif pc==base+0x19ae30:
    index=m.r[5];raw=encode_dialogue(names[index%len(names)],'')[0]+b'\0\0'
    m.store(src,raw);m.r[2]=src;pc=m.r[31]
   else:pc=m.step(pc)
  else:raise AssertionError('Initializer instruction budget')
  for index in range(96):
   target=pool+index*32+0xc34;raw=encode_dialogue(names[index%len(names)],'')[0]+b'\0\0'
   assert m.bytes(target+20,10)==bytes(10),('Initialization metadata overwrite',index)
   assert m.bytes(target,min(len(raw),18))==raw[:18]
   pointer=previous.run(m,base+0x57530,[pool,index]);assert m.bytes(pointer,len(raw))==raw
   cases+=1
 result.update(default_initialization_cases=cases,default_binding_fields_preserved=True)
 return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
