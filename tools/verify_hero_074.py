"""Execute native Hero Tales name/help selectors, including level clamping."""
import json,struct
from sn3_archive import ROOT
from menus_fix_074 import prepare_elf,BASE
from verify_guards_057 import GuardCPU
from dialogue_encoding import encode_dialogue

def verify():
 elf,r=prepare_elf();entries={e['source_address']:e for e in r['entries']};cases=0
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);lo,hi=0x55eac,0x560e0;data=bytearray(elf[192+lo:192+hi])
  for p in range(0,len(data),4):
   w=struct.unpack_from('<I',data,p)[0]
   if w>>26 in (2,3):struct.pack_into('<I',data,p,w&0xfc000000|((w&0x3ffffff)+(base>>2))&0x3ffffff)
  for e in entries.values():
   for ref in e['bindings']:
    if ref['kind']=='hilo' and lo<=ref['high']<hi:
     high,low=ref['high']-lo,ref['low']-lo;va=base+e['new_address']
     for off,value in [(high,(va+0x8000)>>16),(low,va&65535)]:
      w=struct.unpack_from('<I',data,off)[0];struct.pack_into('<I',data,off,w&0xffff0000|value&65535)
  # The untranslated locked-name branch retains its original source pointer.
  va=base+0x216150
  for off,value in [(0x55f90-lo,(va+0x8000)>>16),(0x55f98-lo,va&65535)]:
   w=struct.unpack_from('<I',data,off)[0];struct.pack_into('<I',data,off,w&0xffff0000|value&65535)
  m.store(base+lo,data)
  for level in (-1,0,1,2,3,4,5,6,99):
   for entry,kind in [(lo,'name'),(0x55fdc,'help')]:
    m.r=[0x12400000+i for i in range(32)];m.r[0]=0;m.r[4]=0x09400000;m.r[5]=26
    m.r[29]=0x09f00000;m.r[31]=0x08801234;saved=m.r.copy();pc=base+entry
    for _ in range(200):
     if pc==saved[31]:break
     if pc==base+0x54b14:m.r[2]=level&0xffffffff;pc=m.r[31]
     else:pc=m.step(pc)
    else:raise AssertionError('Hero selector instruction budget')
    for i in list(range(16,24))+[26,27,28,29,30,31]:assert m.r[i]==saved[i]
    index=min(level,5)-1
    if level<=0 and kind=='name':assert m.r[2]==base+0x216150
    else:
     va=0x216100+index*16 if kind=='name' else ([0x21615c,0x216178,0x216190,0x2161ac,0x2161c4][index] if level>0 else 0x2161dc)
     e=entries[va];raw=encode_dialogue(e['english'][0],'')[0]+b'\0\0'
     assert m.r[2]==base+e['new_address'] and m.bytes(m.r[2],len(raw))==raw
    cases+=1
 return dict(passed=True,cases=cases,load_bases=2,level_logic_unchanged=True,locked_name_preserved=True,callback_abi_preserved=True)

if __name__=='__main__':
 r=verify();(ROOT/'work/ui/menus_0.1.74/hero-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
