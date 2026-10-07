"""Read-only execution of the native Status help writer."""
import json,unicodedata
from sn3_archive import ROOT,GameSource
from verify_descriptions_021 import CPU
BASE=ROOT/'work/output/0.1.66'
def run(elf,static,entry,flags):
 c=CPU(elf,static);owner=0x500000;buf=owner+0x19f0
 c.mem[buf-32:buf+210]=b'G'*242;c.r=[0]*32
 c.r[4:10]=[owner,*flags];c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=entry
 for _ in range(100000):
  if pc==0x7ffff0:break
  if pc==0x1c2bc0:
   a,v,n=c.r[4:7];c.mem[a:a+n]=bytes([v&255])*n;c.r[2]=a;pc=c.r[31]
  elif pc==0x1e4ac8:c.r[2]=c.strlen(c.r[4]);pc=c.r[31]
  elif pc==0x1e4b50:
   a,b,n=c.r[4:7];c.mem[a:a+n*2]=c.mem[b:b+n*2];c.r[2]=a;pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError('Instruction budget')
 assert c.mem[buf-32:buf]==b'G'*32 and c.mem[buf+178:buf+210]==b'G'*32
 rows=[];pos=buf
 while c.read(pos,2):
  n=c.strlen(pos);rows.append(unicodedata.normalize('NFKC',c.mem[pos:pos+n*2].decode('cp932')));pos+=n*2+2
 return rows
if __name__=='__main__':
 elf=(BASE/'EBOOT.elf').read_bytes()
 with GameSource(BASE/'Summon_Night_3_EN_0.1.66.iso') as s:
  static=s.resource('02.DAT',3)
  for entry in (0x63774,0x638f8):
   for flags in ((0,1,0,1,0),(0,1,0,0,0),(1,1,0,1,0)):
    print(json.dumps(dict(entry=hex(entry),flags=flags,lines=run(elf,static,entry,flags))))
