"""Execute native equipment formatter and help staging with guarded buffers."""
import json,struct,unicodedata
from verify_descriptions_021 import CPU as BaseCPU,signed
from dialogue_encoding import encode_dialogue
from sn3_archive import ROOT,parse_index,child

class CPU(BaseCPU):
 def __init__(self,elf,static,kind=0):
  super().__init__(elf,static)
  self.kind=kind
  ix=parse_index(static,len(static));data=child(static,ix,15+kind)
  self.mem[0x430000:0x430000+len(data)]=data
  self.count=int.from_bytes(data[:4],'little')
 def run(self,spell,key_item=False):
  owner=0x500000;self.r=[0]*32;self.r[29]=0x700000;self.r[31]=0x7ffff0
  self.r[4]=owner;self.r[5]=self.kind;self.r[6]=spell
  buf=owner+0x19f0;self.mem[buf-32:buf+178+32]=b'G'*(178+64)
  pc=0x64d48;calls=[]
  for step in range(100000):
   if pc==0x7ffff0:break
   if pc==0x199928:self.r[2]=0x430000+4+spell*84;pc=self.r[31]
   elif pc==0x54f08:self.r[2]=int(key_item);pc=self.r[31]
   elif pc==0x1c2bc0:
    a,v,n=self.r[4:7];self.mem[a:a+n]=bytes([v&255])*n;self.r[2]=a;pc=self.r[31]
   elif pc==0x1e4ac8:self.r[2]=self.strlen(self.r[4]);pc=self.r[31]
   elif pc==0x1e4b50:
    a,b,n=self.r[4:7];self.mem[a:a+n*2]=self.mem[b:b+n*2];self.r[2]=a;pc=self.r[31]
   elif pc==0x1e4dd8:
    assert self.r[5:7]==[0,0];v=str(signed(self.r[4]));b=encode_dialogue(v,'')[0]+b'\0\0';self.mem[0x600000:0x600000+len(b)]=b;self.r[2]=0x600000;pc=self.r[31]
   else:
    if pc in (0x1e502c,0x1e4ee0):
     count=self.r[5];chars=sum(self.strlen(p) for p in self.r[6:6+count]);calls.append(chars)
     assert chars+1<48,('Writer temporary overflow',spell,chars)
    pc=self.step(pc)
  else:raise AssertionError(('instruction budget',spell,hex(pc)))
  assert self.mem[buf-32:buf]==b'G'*32 and self.mem[buf+178:buf+210]==b'G'*32,('output overrun',spell)
  lines=[];lengths=[];p=buf
  while self.read(p,2):
   n=self.strlen(p);lengths.append(n);lines.append(unicodedata.normalize('NFKC',self.mem[p:p+n*2].decode('cp932')));p+=n*2+2
  return dict(record=spell,lines=lines,lengths=lengths,total=sum(lengths),max_concat=max(calls,default=0))

def stage(c,payload):
 """Run actual help parser/loops; graphics binding is the test boundary."""
 owner=0x500000;src=0x600000;pool=0x510000
 c.mem[owner:owner+0x1aa8]=bytes(0x1aa8)
 c.mem[src:src+178]=payload
 c.write(owner+0xfc,pool);c.write(owner+0x100,54)
 c.r=[0]*32;c.r[4:10]=[owner,src,0,26,0,0]
 c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x64820;bound=[]
 for step in range(100000):
  if pc==0x7ffff0:break
  if pc==0x634c8:pc=c.r[31] # fresh cleared owner
  elif pc in (0x1c2bc0,0x1c2b80):
   a,v,n=c.r[4:7]
   c.mem[a:a+n]=bytes([v&255])*n if pc==0x1c2bc0 else c.mem[v:v+n]
   c.r[2]=a;pc=c.r[31]
  elif pc in (0x1867c,0x1cbe94,0x1cbdec,0x1cbe48):
   if pc!=0x1867c:
    slot=(c.r[4]-pool)//224
    assert 0<=slot<54,('glyph pool overflow',slot)
    bound.append(slot)
   pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError(('staging instruction budget',hex(pc)))
 return dict(glyphs=c.read(owner+0x40),rows=c.read(owner+0x3c),max_slot=max(bound,default=-1))
