"""Preview source-bound English spell, item, and summoning-menu targets."""
import argparse,json,hashlib,struct
from inspect_categories_069 import ROOT,BASE,collect
from menu_hotfix_017 import lines_at
from battle_elf_refs import references
sha=lambda b:hashlib.sha256(b).hexdigest()
DEST=ROOT/'work/translation/en/categories_0.1.69'
MENUS={
 0x218ec0:['Choose a crafting pair.','ВCrafting List'],
 0x21df5c:['" '],0x21df64:['Set as a favorite?'],
 0x21df80:['Yes','No'],0x21df88:['No'],0x21df90:['" '],
 0x21df98:['Remove from favorites?'],
 0x21dfb4:['Change favorite color','Remove favorite'],
 0x21dfe8:['" '],0x21dff0:[' favorites max.'],
 0x21e028:[' can favorite.'],
 0x21e044:["'Unit Summon' unavailable."],
 0x21e064:[' only.'],
 0x21e080:['Dismiss this summon?','Yes','No'],
 0x21e0a4:['Finish creating summons?','Yes','No'],
}
def prepare():
 rows=collect();bykey={(r['table'],r['slot'],r['source_offset']):r for r in rows};out=[]
 for name,n in [('spells',13),('items',19)]:
  for e in json.loads((DEST/(name+'.json')).read_text())['entries']:
   slot=e.get('slot',8);r=bykey[n,slot,e['source_offset']]
   english=e['english'] if isinstance(e['english'],list) else [e['english']]
   if n==13 and r['records']==[49]:english=['Divine Ixellion']
   out.append({k:v for k,v in r.items() if k!='lines'}|dict(english=english,full_english=e['full_english']))
 b=(BASE/'EBOOT.elf').read_bytes();refs,users,pairs=references(b);menus=[]
 for va,english in MENUS.items():
  pos=va+192;raw=[]
  for _ in english:
   end=pos
   while b[end:end+2]!=b'\0\0':end+=2
   raw.append(b[pos:end]);pos=end+2
  bindings=refs.get(va,[]);assert bindings,(hex(va),'No consumer')
  menus.append(dict(source_address=va,source_sha256=sha(b'\0\0'.join(raw)),source_lines=len(raw),english=english,bindings=bindings))
 for lows,english in [([0x14b994,0x14ba2c,0x14badc],'"'),([0x14bb78],'Only '),([0x14bc44],'Unit Form: ')]:
  va=0x21df58;raw=b[va+192:va+194];selected=[r for r in refs[va] if r.get('low') in lows];assert len(selected)==len(lows)
  menus.append(dict(source_address=va,source_sha256=sha(raw),source_lines=1,english=[english],bindings=selected,selected_consumers=True))
 return dict(version='0.1.69',source_build='0.1.68',entries=out,menus=menus)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--refresh',action='store_true');a=p.parse_args();r=prepare()
 print(json.dumps(dict(mode='write' if a.write else 'preview',table_fields=len(r['entries']),menus=r['menus'],samples=r['entries'][:4]+r['entries'][191:196]),indent=2))
 if a.write or a.refresh:
  target=DEST/'targets.json';assert not (ROOT/'work/output/0.1.69/manifest.json').exists();assert a.refresh or not target.exists();target.write_text(json.dumps(r,indent=2)+'\n')
