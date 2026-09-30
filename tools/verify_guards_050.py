"""Exercise emitted guards, including relocation and all 65,536 glyph cells."""
import struct
from verify_descriptions_021 import CPU as BaseCPU
from verify_font_patch import Machine
from stability_049 import prepare_elf,HELP_SITE,GLYPH_SITE
from dialogue_encoding import encode_dialogue

class AliasCPU(BaseCPU):
 def address(self,a):return a-0x08800000 if 0x08800000<=a<0x0a000000 else a
 def read(self,a,n=4):return super().read(self.address(a),n)
 def write(self,a,v,n=4):return super().write(self.address(a),v,n)

def stage(c,payload):
 owner=0x08d00000;src=0x08e00000;pool=0x08d10000
 c.mem[0x500000:0x501aa8]=bytes(0x1aa8)
 c.mem[0x600000:0x600000+len(payload)]=payload
 c.write(owner+0xfc,pool);c.write(owner+0x100,54)
 c.r=[0]*32;c.r[4:10]=[owner,src,0,26,0,0]
 c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=HELP_SITE;bound=[]
 for _ in range(100000):
  if pc==0x7ffff0:break
  if pc==0x634c8:pc=c.r[31]
  elif pc in (0x1c2bc0,0x1c2b80):
   a,v,n=c.r[4:7];aa=c.address(a)
   c.mem[aa:aa+n]=bytes([v&255])*n if pc==0x1c2bc0 else c.mem[c.address(v):c.address(v)+n]
   c.r[2]=a;pc=c.r[31]
  elif pc in (0x1867c,0x1cbe94,0x1cbdec,0x1cbe48):
   if pc!=0x1867c:
    slot=(c.r[4]-pool)//224;assert 0<=slot<54,('glyph pool overflow',slot);bound.append(slot)
   pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError(('staging budget',hex(pc)))
 return dict(glyphs=c.read(owner+0x40),rows=c.read(owner+0x3c),max_slot=max(bound,default=-1))

class GuardCPU(Machine):
 step=BaseCPU.step
 @property
 def r(self):return self.reg
 @r.setter
 def r(self,value):self.reg=value
 def read(self,a,n=4):return super().read(a,n)
 def write(self,a,v,n=4):self.store(a,(v&((1<<(n*8))-1)).to_bytes(n,'little'))
 def until(self,pc,stop):
  for _ in range(2000):
   if pc==stop:return
   pc=self.step(pc)
  raise AssertionError('Guard instruction budget')

def verify(elf,static):
 expected,report=prepare_elf()
 from stages_pupil_names import parse_elf
 prior_seg=parse_elf(expected)['phdrs'][3];current_seg=parse_elf(elf)['phdrs'][3]
 assert elf[current_seg[1]:current_seg[1]+prior_seg[4]]==expected[prior_seg[1]:prior_seg[1]+prior_seg[4]],'Inherited guard code changed'
 for site in (HELP_SITE,GLYPH_SITE):assert elf[site+192:site+200]==expected[site+192:site+200]
 report['added_segment_file_offset']=current_seg[1];report['added_segment_bytes']=current_seg[4]
 diag=int(report['diagnostic_address'],16);code=int(report['code_address'],16)
 # Full native staging must preserve legal output and contain malformed output.
 c=AliasCPU(elf,static);native=[]
 for lengths,reject in [([27,27],False),([18,18,18],False),([28],True),([27,27,1],True),([1],False),([],False)]:
  payload=b''.join(encode_dialogue('A'*n,'')[0]+b'\0\0' for n in lengths)+b'\0\0'
  before=c.read(diag);r=stage(c,payload)
  assert c.read(diag)-before==int(reject),(lengths,r)
  assert r['glyphs']==(10 if reject else sum(lengths)),(lengths,r)
  native.append(dict(lengths=lengths,rejected=reject,**r))
 help_cases=0;glyph_cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,report,base)
  for site in (HELP_SITE,GLYPH_SITE):
   w=struct.unpack_from('<I',elf,site+192)[0]
   w=(w&0xfc000000)|(((w&0x3ffffff)+(base>>2))&0x3ffffff)
   m.store(base+site,struct.pack('<I',w)+elf[site+196:site+200])
  d=base+diag;source=0x09800000;owner=0x09400000
  cases=[(source,[27,27],0),(source,[18,18,18],0),(source,[28],1),(source,[27,27,1],1),
         (source,[],0),(0,[],0),(source+1,[],2),(0x508,[],2),(0x0a000000,[],2),
         (0xfffffffe,[],2),(0x09fffffe,[1],2),(source,[1,1,1,80],0)]
  for ptr,lengths,reason in cases:
   payload=b''.join(encode_dialogue('A'*n,'')[0]+b'\0\0' for n in lengths)+b'\0\0'
   if ptr in (source,0x09fffffe):m.store(ptr,payload if ptr==source else payload[:2])
   m.store(d,bytes(16));m.r=[0x12500000+i for i in range(32)];m.r[0]=0
   m.r[4:10]=[owner,ptr,2,26,77,1];m.r[29]=0x09f00000;m.r[31]=0x08801234
   saved=m.r.copy();m.until(base+HELP_SITE,base+0x64828)
   assert m.r[31]==saved[31] and m.r[29]==saved[29]-0x90
   for i in list(range(2,5))+list(range(6,10))+list(range(16,24))+[26,27,28,30]:assert m.r[i]==saved[i],(i,reason)
   assert m.read(owner+0x19e0)==77,'Displaced delay-slot store lost'
   assert m.read(d)==int(bool(reason)) and m.read(d+8)==reason
   assert m.r[5]==(d+16 if reason else ptr)
   help_cases+=1
  for cell in range(65536):
   lo=cell&255;hi=cell>>8;valid=(0x81<=lo<=0x9f or 0xe0<=lo<=0xfc) and 0x40<=hi<=0xfc and hi!=0x7f
   m.store(d,bytes(16));m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4]=cell;m.r[18]=owner
   m.write(owner,cell,2);saved=m.r.copy();m.until(base+GLYPH_SITE,base+0x1d8f60)
   assert m.r[4]==(cell if valid else 0x4881),(base,cell)
   assert m.r[5]==((m.r[4]&255)-128)&0xffffffff
   assert m.read(d+4)==int(not valid) and m.read(owner,2)==m.r[4]
   for i in [2,3,6,7]+list(range(10,31)):assert m.r[i]==saved[i],(cell,i)
   glyph_cases+=1
 return dict(relocated_help_cases=help_cases,glyph_cases=glyph_cases,load_bases=2,native_staging=native,
             diagnostic_address=hex(diag),limitations='Guards cover two text paths, not all pointers or allocations.')
