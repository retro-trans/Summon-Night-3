"""Check heading dispatch plus all existing saved-name mappings in emitted code."""
import json,struct
from magic_heading_033 import prepare_elf,LIST
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from list_vwf_020 import name_pairs

def verify():
 data,r=prepare_elf();r=r['heading'];count=0;pairs,_,audit=name_pairs()
 for base in [0x08804000,0x0890c000]:
  for allocated,text_present in [(False,False),(False,True),(True,False),(True,True)]:
   c=CPU(data,r,base);obj=0x09000000;src=obj+0x1000;c.store(obj,bytes(256));c.store(obj+0xc0,struct.pack('<I',obj+0x2000 if allocated else 0));c.store(src,b'\x83\x68\x83\x8a\x83\x67\x83\x8b\0\0')
   c.set('a0',obj);c.set('a1',src if text_present else 0);c.set('a2',77);seen=[]
   def bind(m):seen.append(('vwf',m.reg[4:7]));return {'v0':9}
   def native(m):seen.append(('native',m.reg[4:7]));return {'v0':7}
   c.native_handlers={base+LIST:bind,base+0x1cbee0:native};c.run(int(r['code_address'],16)-CODE_VA+r['labels']['heading'])
   good=allocated and text_present;assert seen==[('vwf' if good else 'native',[obj,src if text_present else 0,1 if good else 77])];count+=1
  for src,dst in pairs+[(b'Custom',b'Custom'),('テスト'.encode('cp932'),'テスト'.encode('cp932'))]:
   c=CPU(data,r,base);ptr=0x09000000;c.store(ptr,src+b'\0\0');c.set('a0',ptr);c.run(0x3489b8-CODE_VA)
   assert c.bytes(c.reg[2],len(dst)+2)==dst+b'\0\0';assert c.bytes(ptr,len(src)+2)==src+b'\0\0';count+=1
 return dict(cases=count,load_bases=2,default_name_mappings=len(pairs),coverage=['heading dispatch','null and unallocated native fallback','all existing name mappings','custom-name passthrough','source strings unchanged'])
if __name__=='__main__':print(json.dumps(verify(),indent=2))
