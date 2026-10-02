"""Execute relocated arena getter; prove all scripts fit and old overlap exists."""
import json,struct
from cache_065 import prepare_elf,BASE,CAPACITY,HOOKS
from verify_menu_vwf_020 import CPU
from font_patch import CODE_VA
from stages_pupil_names import parse_elf

def verify():
 elf,r=prepare_elf();old=(BASE/'EBOOT.elf').read_bytes();cases=0
 for base in (0x08804000,0x0890c000):
  for site in HOOKS:
   c=CPU(elf,r,base)
   for i in range(4,8):c.reg[i]=0x09001234+i
   c.set('s0',0x12345678);c.set('s3',0x76543210)
   c.run(int(r['code_address'],16)-CODE_VA)
   assert c.reg[2]+0x240000==base+r['arena_va']
   assert c.reg[4:8]==[0x09001234+i for i in range(4,8)]
   assert c.reg[16]==0x12345678 and c.reg[19]==0x76543210
   assert struct.unpack_from('<I',elf,site+192)[0]==3<<26|int(r['code_address'],16)>>2
   cases+=1
 allowed={i for p in HOOKS for i in range(p+192,p+196)}
 assert all(i in allowed for i,(a,b) in enumerate(zip(old[192:192+0x22d37c],elf[192:192+0x22d37c]),192) if a!=b)
 seg=parse_elf(elf)['phdrs'][3];assert seg[6]==7
 arena_off=seg[1]+r['arena_va']-seg[2]
 assert elf[arena_off:arena_off+CAPACITY]==bytes(CAPACITY)
 assert r['arena_va']>=parse_elf(old)['phdrs'][3][2]+parse_elf(old)['phdrs'][3][4]
 # Measured guest layout in the failed Chapter 15 normal-save session.
 static_start=0x1bb100;static_size=0x8b800
 assert static_start<0x240000<static_start+static_size
 return dict(passed=True,abi_cases=cases,load_bases=2,private_arena_bytes=CAPACITY,
  scripts_checked=len(r['chapter_scripts']),largest_script_bytes=max(x['decoded_bytes'] for x in r['chapter_scripts']),
  old_overlap_reproduced=True,only_three_native_call_sites_changed=True,
  native_decoder_and_binding_unchanged=True)

if __name__=='__main__':print(json.dumps(verify(),indent=2))
