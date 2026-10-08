"""Execute menu/banner routing and verify every native encounter title import."""
import json,struct
from sn3_archive import ROOT,GameSource,parse_v4,child
from battle_fix_077 import prepare_elf,prepare_tables,BASE,sha
from battle_art_077 import prepare
from verify_guards_050 import GuardCPU

def verify():
 elf,r=prepare_elf();cases=[]
 for base in (0x08804000,0x0890c000):
  m=GuardCPU(elf,r,base);owner=0x09400000
  for count,start,left,right in [(4,0,0,0),(1,0,0,0),(1,0,1,0),(1,0,0,1),(1,0,1,1),(1,1,1,1),(0,0,1,1),(8,0,1,1)]:
   m.store(owner,bytes(0x100))
   for off,value in [(0x3c,count),(0x20,start),(0x4c,left),(0x50,right)]:m.write(owner+off,value)
   m.r=[0x12500000+i for i in range(32)];m.r[0]=0;m.r[4:8]=[0x09500000,0x09600000,1,77];m.r[22]=owner;m.r[29]=0x09f00000;m.r[31]=0x08801234
   before=m.r.copy();center=count==1 and start==0 and bool(left) and bool(right)
   stop=base+(0x35283c if center else 0x34a0c8)
   m.until(base+int(r['code_address'],16)+r['labels']['list_or_banner'],stop)
   assert m.r[4:8]==before[4:8] and m.r[16:32]==before[16:32]
   cases.append(dict(base=hex(base),rows=count,start=start,left_context=left,right_context=right,centered_banner=center))
 with GameSource(BASE/'Summon_Night_3_EN_0.1.76.iso') as s:
  _,_,_,messages=prepare_tables(s);art,ar=prepare(s,True)
  # Optional cards share English conditions, which remain byte-identical.
  for n,b in art['01.DAT'].items():
   old=s.resource('01.DAT',n);oi=parse_v4(old);ni=parse_v4(b)
   assert all(child(old,oi,k)==child(b,ni,k) for k in range(oi['count']) if k!=4)
 report=dict(version='0.1.77',passed=True,routing_cases=cases,skill_list_left_aligned=True,animation_centering_preserved=True,crafting_messages=messages['existing_crafting_prompts_verified'],title_import=ar,original_pools_preserved=True)
 folder=ROOT/'work/ui/battle_0.1.77';folder.mkdir(exist_ok=True);(folder/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 build=ROOT/'work/output/0.1.77'
 if (build/'manifest.json').exists():
  manifest=json.loads((build/'manifest.json').read_text());assert sha(elf)==sha((build/'EBOOT.elf').read_bytes());report['iso_sha256']=manifest['output_sha256'];(build/'battle-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(passed=True,routing_cases=len(cases),title_sprites=ar['translated_sprites'],crafting_groups=len(messages['existing_crafting_prompts_verified']))))
if __name__=='__main__':verify()
