"""Native Pact name and description execution; scoped VWF call verification."""
import json,struct,unicodedata
from verify_descriptions_021 import CPU
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue

def text_at(c,p):
 n=c.strlen(p);return unicodedata.normalize('NFKC',c.mem[p:p+n*2].decode('cp932'))

def verify(elf,static):
 c=CPU(elf,static);names=[];helps=[]
 for mask in range(1,16):
  c.mem[0x580000:0x580004]=bytes(bool(mask&(1<<n)) for n in range(4));c.r=[0]*32;c.r[4]=0x580000;c.r[31]=0x7ffff0;pc=0x695c8
  for _ in range(1000):
   if pc==0x7ffff0:break
   pc=c.step(pc)
  else:raise AssertionError('name loop')
  text=text_at(c,c.r[2]);assert text.startswith('Pact: ') and len(text)<=16,(mask,text)
  names.append(dict(mask=mask,text=text))
 for mask in range(1,32):
  # Execute the native writer initialization, then the isolated Pact case.
  c.r=[0]*32;c.r[4]=0x500000;c.r[6]=0x3f1;c.r[29]=0x700000;c.r[31]=0x7ffff0
  buf=0x5019f0;c.mem[buf-32:buf+210]=b'G'*242
  pc=0x65f2c
  for step in range(10000):
   if pc==0x65fc4:pc=0x6688c
   if pc==0x66a8c:break
   if pc==0x1c2bc0:
    a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
   elif pc==0x3d774:c.r[2]=int(bool(mask&(1<<c.r[5])));pc=c.r[31]
   elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
   elif pc==0x1e4b50:
    a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
   else:pc=c.step(pc)
  else:raise AssertionError(('formatter loop',mask,hex(pc)))
  assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
  lines=[];p=buf
  while c.read(p,2):
   s=text_at(c,p);lines.append(s);p+=c.strlen(p)*2+2
  assert len(lines)<=2 and max(map(len,lines))<=27,(mask,lines)
  assert all(line not in [']','['] for line in lines),(mask,lines)
  helps.append(dict(mask=mask,lines=lines))
 for site in [0x145f74,0x146364,0x146398,0x1463b0,0x146fcc]:
  assert struct.unpack_from('<I',elf,site+192)[0]==3<<26|0x347b5c>>2
 return dict(native_pact_names=names,native_pact_help=helps,vwf_call_sites=5,output_guards=True,exact_unlock_screen_verified=False)
if __name__=='__main__':
 from skills_041 import prepare_elf,prepare_tables,BASE
 from sn3_archive import GameSource
 elf,_=prepare_elf()
 with GameSource(next(BASE.glob('*.iso'))) as source:tables,_,_,_=prepare_tables(source)
 r=verify(elf,tables[3]);print(json.dumps(r,indent=2))
