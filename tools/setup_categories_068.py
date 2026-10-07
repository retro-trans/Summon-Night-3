"""Preview and save English map labels bound to the current native pointers."""
import argparse,json,struct
from categories_fix_068 import ROOT,BASE,MAP,sha
NAMES={0x21cf98:'Rocky Shore',0x21cfa0:'Forest',0x21cfa4:'Hideout Outskirts',0x21cfb0:'Dragonbone Fault',0x21cfbc:'Dawn Hill',0x21cfc4:'Abandoned Mine',0x21cfcc:'Gate of Evocation',0x21cfd8:'Dusk Gravestone'}
SHORT={0x21cfa4:'Hideout Edge',0x21cfb0:'Dragon Rift',0x21cfc4:'Aband. Mine',0x21cfcc:'Evoc. Gate',0x21cfd8:'Dusk Grave'}
def prepare():
 b=(BASE/'EBOOT.elf').read_bytes();groups={}
 for f in range(0x229530,0x2295bc,4):
  p=struct.unpack_from('<I',b,f+192)[0]
  if not p:continue
  end=b.index(b'\0',p+192)
  text=b[p+192:end].decode('cp932')
  if p in NAMES:english=NAMES[p]
  elif text.startswith('第') and text.endswith('界廊'):english='Hall '+text[1:-2]
  else:continue
  if p not in groups:groups[p]=dict(source_address=p,source_sha256=sha(b[p+192:end]),english=SHORT.get(p,english),full_english=english,pointer_fields=[])
  groups[p]['pointer_fields'].append(f)
 assert len(groups)==24,len(groups)
 return dict(version='0.1.68',entries=list(groups.values()),terminology_note='Gate of Evocation and Hall follow existing glossary; other locations are literal English renderings.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--refresh',action='store_true');a=p.parse_args();r=prepare();print(json.dumps(dict(mode='write' if a.write or a.refresh else 'preview',**r),indent=2))
 if a.write or a.refresh:
  assert not (ROOT/'work/output/0.1.68/manifest.json').exists();assert a.refresh or not MAP.exists();MAP.parent.mkdir(parents=True,exist_ok=True);MAP.write_text(json.dumps(r,indent=2)+'\n')
