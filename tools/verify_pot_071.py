"""Execute the patched native name setter/getter and protect animation fields."""
import json,struct
from pot_fix_071 import prepare_elf,SLOTS,STRIDE,BASE
from verify_guards_057 import GuardCPU
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT
def run(m,entry,args):
 m.r=[0x12400000+i for i in range(32)];m.r[0]=0;m.r[4:4+len(args)]=args;m.r[29]=0x09f00000;m.r[31]=0x08801234
 saved=m.r.copy();pc=entry
 for _ in range(10000):
  if pc==saved[31]:break
  if pc==m.base+0x1c2bc0:
   m.store(m.r[4],bytes([m.r[5]&255])*m.r[6]);pc=m.r[31]
  else:pc=m.step(pc)
 else:raise AssertionError(('instruction budget',hex(pc)))
 for i in list(range(16,24))+[26,27,28,29,30,31]:assert m.r[i]==saved[i],('ABI register',i)
 return m.r[2]
def verify():
 elf,r=prepare_elf();tests=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base)
  for lo,hi in ((0x57530,0x57540),(0x57540,0x575d4)):
   data=bytearray(elf[192+lo:192+hi])
   for p in range(0,len(data),4):
    w=struct.unpack_from('<I',data,p)[0]
    if w>>26 in (2,3):struct.pack_into('<I',data,p,w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff)
   m.store(base+lo,data)
  pool=0x09400000;src=0x09800000
  cases=['Summon Mate','Stonework Base','Colossus Form','Shine Saber','R','CUSTOMXX','A'*31,'Japanese']
  payloads=[encode_dialogue(s,'')[0]+b'\0\0' for s in cases]+['テコ　　'.encode('cp932')+b'\0\0',b'\0\0']
  for index in range(SLOTS):
   target=pool+index*32+0xc34;raw=payloads[index%len(payloads)];trim=raw[:-2]
   while trim.endswith(b'\x81\x40'):trim=trim[:-2]
   trim=trim[:62]+b'\0\0';m.store(src,raw)
   m.store(target,bytes(20)+b'\x4c\x00\x01\x01\x01\x01\x00\x00'+b'GUARD')
   guard=m.bytes(target+20,12)
   run(m,base+0x57540,[pool,index,src])
   assert m.bytes(target+20,12)==guard,('Animation fields changed',index)
   prefix=trim[:-2][:18]+b'\0\0';assert m.bytes(target,len(prefix))==prefix
   pointer=run(m,base+0x57530,[pool,index]);assert m.bytes(pointer,len(trim))==trim,(index,hex(pointer))
   tests+=1
  # Rename a slot, reload its native save prefix, and reject a changed custom name.
  index=76;target=pool+index*32+0xc34
  raw=encode_dialogue('Summon Mate','')[0]+b'\0\0';m.store(src,raw)
  run(m,base+0x57540,[pool,index,src]);pointer=run(m,base+0x57530,[pool,index]);assert m.bytes(pointer,len(raw))==raw
  m.store(target,raw[:18]+b'\0\0');assert run(m,base+0x57530,[pool,index])==pointer
  m.store(target,encode_dialogue('Custom','')[0]+bytes(8));assert run(m,base+0x57530,[pool,index])==target
  m.store(src,encode_dialogue('R','')[0]+b'\0\0');run(m,base+0x57540,[pool,index,src]);pointer=run(m,base+0x57530,[pool,index]);assert m.bytes(pointer,8)==encode_dialogue('R','')[0]+bytes(6)
  tests+=4
 return dict(passed=True,load_bases=2,native_setter_getter_cases=tests,animation_fields_preserved=True,full_names_preserved=True,save_prefix_reload=True,custom_name_fallback=True)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
