"""Preview native skill formatter translations and construct new build tools."""
import argparse,json,hashlib
from sn3_archive import ROOT
from battle_elf_refs import references
BASE=ROOT/'work/output/0.1.69';DEST=ROOT/'work/translation/en/categories_0.1.70'
TEXT={0x217300:'Counter chance +',0x21730c:'Weapon ailment chance +',0x217328:'Ailment chance +',0x21733c:'Rarely KOs foes on a crit.',0x217360:'Lowers enemy counter chance',0x217374:'2-square piercing attack',0x217384:'Vertical attack range +1',0x217398:'Adds Snipe effect',0x2173ac:'Halves distance penalty',0x2173f8:'Dragon/humanoid transform.',0x217410:'Uses left: ',0x217418:''}

def prepare():
 b=(BASE/'EBOOT.elf').read_bytes();refs,_,_=references(b);menus=[]
 review=json.loads((ROOT/'work/scratch/categories070-review.json').read_text())
 for va,en in TEXT.items():
  p=va+192;z=p
  while b[z:z+2]!=b'\0\0':z+=2
  assert refs.get(va),hex(va)
  rr=next(x for x in review['formatter_reviews'] if int(x['va'],16)==va)
  menus.append(dict(source_address=va,source_sha256=hashlib.sha256(b[p:z]).hexdigest(),source_lines=1,english=[en],full_english=rr['full_english'],bindings=refs[va]))
 return dict(version='0.1.70',source_build='0.1.69',entries=[],menus=menus,stat_help_note='HP/MP, six stats and four affinity resistance helps are already English in 0.1.69; retain and verify those pointers.',startup_notice=dict(resource_path=[25,0],heading='Notice',english='Distributing game software online without permission from the rights holder, or knowingly downloading an illegally distributed copy, is strictly prohibited by law. Thank you for your understanding and cooperation.'))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--tools',action='store_true');a=p.parse_args();r=prepare();print(json.dumps(r,indent=2))
 if a.write:
  DEST.mkdir(parents=True,exist_ok=False);(DEST/'targets.json').write_text(json.dumps(r,indent=2)+'\n')
 if a.tools:
  assert not (ROOT/'work/output/0.1.70').exists()
  for name in ['categories_fix','build_categories','verify_stability','categories_runtime']:
   old=ROOT/'tools'/f'{name}_069.py';s=old.read_text()
   s=s.replace('0.1.68','BASE_OLD').replace('0.1.69','0.1.70').replace('BASE_OLD','0.1.69')
   s=s.replace('_068','_PRIOR_').replace('_069','_070').replace('_PRIOR_','_069').replace('categories069','categories070').replace('19406','19407')
   if name=='build_categories':s=s.replace("'inspect_categories_070.py',",'')
   target=ROOT/'tools'/f'{name}_070.py';assert not target.exists();target.write_text(s)
  s=(ROOT/'tools/launch_categories_069.ps1').read_text().replace('069','070').replace('0.1.69','0.1.70').replace('19406','19407');(ROOT/'tools/launch_categories_070.ps1').write_text(s)
