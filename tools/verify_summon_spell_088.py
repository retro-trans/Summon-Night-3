"""Exercise the unchanged native cache allocator with old and corrected captions."""
import json,struct
from sn3_archive import ROOT,GameSource
from verify_descriptions_021 import CPU
from dialogue_encoding import encode_dialogue
from verify_guards_050 import GuardCPU

def banners(elf,expected):
 prior=json.loads((ROOT/'work/output/0.1.87/manifest.json').read_text('utf8'))['banner086_fix'];matches=0
 for base in (0x08804000,0x0890c000):
  c=GuardCPU(elf,prior,base)
  for sample in expected+['Crush! L.Gen.Sword','Crush! L.G.Sword extra','Crush! L.G.Swor','']:
   c.store(0x09600000,(encode_dialogue(sample,'')[0] if sample else b'')+bytes(2));c.r=[0]*32;c.r[4]=0x09600000;c.r[31]=0x08801234
   pc=base+int(prior['code_address'],16)+prior['labels']['match']
   for _ in range(100000):
    if pc==0x08801234:break
    pc=c.step(pc)
   else:raise AssertionError('Banner lookup instruction budget')
   assert c.r[2]==(len(sample) if sample in expected else 0),sample
   matches+=1
 return matches

def allocate(c,text):
 manager,table,obj,src,pool=0x500000,0x510000,0x520000,0x530000,0x540000
 c.mem[manager:pool+64]=bytes(pool+64-manager)
 c.write(0x22a340,manager);c.write(manager+8,table)
 for offset,fn in [(40,0x600000),(48,0x600004),(80,0x600008)]:
  c.write(table+offset,0,2);c.write(table+offset+4,fn)
 c.mem[pool:pool+24]=struct.pack('<12H',0,0,8,0,128,0,8,0,0,16,16,0)
 raw=encode_dialogue(text,'')[0]+bytes(2);c.mem[src:src+len(raw)]=raw
 c.r=[0]*32;c.r[4:7]=[obj,src,1];c.r[29]=0x700000;c.r[31]=0x7ffff0;pc=0x1cbdec
 for _ in range(10000):
  if pc==0x7ffff0:break
  if pc in (0x600000,0x600004,0x600008,0x1e4ac8):
   c.r[2]={0x600000:pool,0x600004:3,0x600008:0,0x1e4ac8:len(text)}[pc];pc=c.r[31]
  else:pc=c.step(pc)
 else:raise AssertionError('Native allocator instruction budget')
 return c.read(obj+0xc0)!=0

def main():
 folder=ROOT/'work/output/0.1.88';m=json.loads((folder/'manifest.json').read_text('utf8'));r=m['summon_spell088_fix']
 elf=(folder/'EBOOT.elf').read_bytes()
 with GameSource(folder/m['output_iso']) as s:c=CPU(elf,s.resource('02.DAT',3))
 change=r['changes'][0]
 assert not allocate(c,change['before'])
 assert allocate(c,change['after'])
 for row in r['width_audit']:assert allocate(c,row['text']),row
 result=dict(passed=True,version='0.1.88',iso_sha256=m['output_sha256'],native_allocator_executed=True,
  old_caption_allocation_failed=True,corrected_caption_allocation_succeeded=True,spell_names_checked=len(r['width_audit']),
  cache_fixture_capacities=[8,8,16],boundary_stubs=['font manager pool/count accessors','allocation counter','U16 text length'],
  banner_lookup_cases=banners(elf,r['banner_lookup']['banner_names']),banner_lookup_load_bases=2,
  runtime_rendering_verified_separately=True)
 p=ROOT/'work/ui/ui_0.1.88/native-cache-validation.json';p.write_text(json.dumps(result,indent=2)+'\n','utf8',newline='\n')
 print(json.dumps(result),flush=True)

if __name__=='__main__':main()
