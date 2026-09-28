"""Execute the game's unchanged spell formatter and writer, including delay slots.

Only memset, U16 memcpy/length and numeric formatting are boundary stubs.
No synthetic substitute for the description formatting or line-wrap logic.
"""
import struct,json,unicodedata
from sn3_archive import ROOT,GameSource,child,parse_index
from stages_pupil_names import parse_elf
from dialogue_encoding import encode_dialogue

def signed(x,b=32):return x-(1<<b) if x&(1<<(b-1)) else x

class CPU:
 def __init__(self,elf,static):
  self.mem=bytearray(0x800000);self.r=[0]*32;self.lo=0;self.hi=0
  for h in parse_elf(elf)['phdrs']:
   if h[0]==1:self.mem[h[2]:h[2]+h[4]]=elf[h[1]:h[1]+h[4]]
  ix=parse_index(static,len(static));self.tables={};pos=0x400000
  index=json.loads((ROOT/'work/translation/en/interface.index.json').read_text())
  for n in (1,13):
   b=child(static,ix,n);self.mem[pos:pos+len(b)]=b
   t=next(t for t in index['tables'] if t['resource_path']==[3,n]);self.tables[n]=(pos,t)
   for rec in range(t['record_count']):
    for slot in t['pointer_slots']:
     f=pos+4+rec*t['record_stride']+slot*4;v=self.read(f)
     if v:self.write(f,v+pos)
   pos+=0x10000
  p,t=self.tables[13]
  for rec in range(t['record_count']):self.write(0xa4684+rec*4,p+4+rec*40)
  self.write(0xa56cc,self.tables[1][0]+4)
 def read(self,a,n=4):
  assert 0<=a<=len(self.mem)-n,hex(a)
  return int.from_bytes(self.mem[a:a+n],'little')
 def write(self,a,v,n=4):
  assert 0<=a<=len(self.mem)-n,hex(a)
  self.mem[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 def strlen(self,a):
  n=0
  while self.read(a+n*2,2):n+=1;assert n<1000
  return n
 def step(self,pc,delay=False):
  w=self.read(pc);op=w>>26;rs=w>>21&31;rt=w>>16&31;rd=w>>11&31;fn=w&63;sa=w>>6&31
  x,y=self.r[rs],self.r[rt];imm=signed(w&65535,16);nextpc=pc+4;branch=None;likely=False
  if op==0:
   if fn==0:self.r[rd]=y<<sa
   elif fn==2:self.r[rd]=y>>sa
   elif fn==3:self.r[rd]=signed(y)>>sa
   elif fn==4:self.r[rd]=y<<(x&31)
   elif fn==6:self.r[rd]=y>>(x&31)
   elif fn in (8,9):
    branch=x
    if fn==9:self.r[rd]=pc+8
   elif fn in (0x20,0x21):self.r[rd]=x+y
   elif fn in (0x22,0x23):self.r[rd]=x-y
   elif fn==0x24:self.r[rd]=x&y
   elif fn==0x25:self.r[rd]=x|y
   elif fn==0x26:self.r[rd]=x^y
   elif fn==0x2a:self.r[rd]=int(signed(x)<signed(y))
   elif fn==0x2b:self.r[rd]=int(x<y)
   elif fn in (0x18,0x19):
    v=(signed(x)*signed(y) if fn==0x18 else x*y)&0xffffffffffffffff;self.lo=v&0xffffffff;self.hi=v>>32
   elif fn==0x12:self.r[rd]=self.lo
   elif fn==0x10:self.r[rd]=self.hi
   else:raise AssertionError((hex(pc),hex(w)))
  elif op in (2,3):
   branch=(pc+4)&0xf0000000|(w&0x3ffffff)<<2
   if op==3:self.r[31]=pc+8
  elif op in (1,4,5,6,7,20,21,22,23):
   if op==1:cond=signed(x)<0 if rt in (0,2) else signed(x)>=0;likely=rt in (2,3)
   else:
    o=op-16 if op>=20 else op;likely=op>=20
    cond={4:x==y,5:x!=y,6:signed(x)<=0,7:signed(x)>0}[o]
   if cond:branch=pc+4+imm*4
   elif likely:nextpc=pc+8
   else:branch=pc+8
  elif op in (8,9):self.r[rt]=x+imm
  elif op==10:self.r[rt]=int(signed(x)<imm)
  elif op==11:self.r[rt]=int(x<(imm&0xffffffff))
  elif op==12:self.r[rt]=x&(w&65535)
  elif op==13:self.r[rt]=x|(w&65535)
  elif op==14:self.r[rt]=x^(w&65535)
  elif op==15:self.r[rt]=(w&65535)<<16
  elif op in (32,33,35,36,37):
   n={32:1,33:2,35:4,36:1,37:2}[op];v=self.read((x+imm)&0xffffffff,n);self.r[rt]=signed(v,n*8) if op in (32,33) else v
  elif op in (40,41,43):self.write((x+imm)&0xffffffff,y,{40:1,41:2,43:4}[op])
  else:raise AssertionError((hex(pc),hex(w)))
  self.r=[v&0xffffffff for v in self.r];self.r[0]=0
  if branch is not None:
   assert not delay,'Branch in delay slot';self.step(pc+4,True);return branch
  return nextpc
 def run(self,spell):
  owner=0x500000;self.r=[0]*32;self.r[29]=0x700000;self.r[31]=0x7ffff0
  self.r[4]=owner;self.r[6]=spell
  buf=owner+0x19f0;self.mem[buf-32:buf+178+32]=b'G'*(178+64)
  pc=0x658e8;calls=[]
  for step in range(100000):
   if pc==0x7ffff0:break
   if pc==0x1c2bc0:
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
  lines=[];p=buf
  while self.read(p,2):
   n=self.strlen(p);lines.append(unicodedata.normalize('NFKC',self.mem[p:p+n*2].decode('cp932')));p+=n*2+2
  return dict(record=spell,lines=lines,lengths=list(map(len,lines)),total=sum(map(len,lines)),max_concat=max(calls,default=0))

def verify(elf,static):
 c=CPU(elf,static);p,t=c.tables[13];results=[]
 for rec in range(1,t['record_count']):
  if c.read(p+4+rec*40+32):results.append(c.run(rec))
 return results

if __name__=='__main__':
 import sys
 folder=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'work/output/0.1.20')
 with GameSource(next(folder.glob('*.iso'))) as src:r=verify((folder/'EBOOT.elf').read_bytes(),src.resource('02.DAT',3))
 print(json.dumps(r,ensure_ascii=False,indent=2))
