"""Apply explicit human wording decisions; preview before --write."""
import json,argparse
from sn3_archive import ROOT
F=ROOT/'work/translation/en/status_0.1.18'
# Exact index identities, never substring substitutions or phonetic conversion.
WEAPONS={
0x81c4:'Blind Dagger',0x81d4:'Carving Knife',0x8220:'Assassins',0x823a:'Bind Edge',0x824a:'Ray Edge',
0x82fa:'Blind Saber',0x831a:'Brawler Saber',0x832c:'Threshold',0x8448:'Heartbreaker',0x845a:'Overlord',0x8474:'Soulbreaker',
0x84d6:'High Blade',0x84f4:'Storm Blade',
0x8512:'Mighty Blade',0x8540:'Wraith Slater',0x856a:'Giga Slayer',0x8586:'Stella Strike',
0x8598:'Million Death',0x85a8:'Knight of Night',0x85cc:'Billion Death',0x86a6:'Pirate Axe',0x86b8:'Brawler Axe',
0x87ac:'Holly Staff',0x87b4:'Tri Rod',0x87e8:'Star Rod',0x87f6:'Black Rod',0x8806:'Cat Wand',0x881c:'Lapis Rod',
0x882a:'Flower Rod',0x8870:'Spiral Rod',0x88ce:'Flag Spear',0x8912:'Silent Lance',0x894a:'Crescent Lance',0x895c:'Dark Spine',
0x8afa:'Eagle Claw',0x8b0a:'Iron Claw',0x8b1a:'Jackal Claw',0x8b44:'Gray Fang',0x8b66:'Tiger Claw',0x8b76:'Snake Bite',0x8b92:'Wraith Fang',
0x8bc8:'Screamer',0x8bd4:'Plasma Drill',0x8be4:'Drill Phantom',0x8c06:'Silver Drill',
0x8c80:'Blind Needle',0x8c92:'Paralyze Needle',0x8ca4:'Silence Needle',0x8cbe:'Squid Ink Throw',0x8cce:'Hard Picker',0x8d2a:'Basilisk Needle',0x8d46:'Joker Throw',
0x8d7c:'Crossbow',0x8d88:'Flower Bow',0x8d96:'Zel Crossbow',0x8db0:'Strike Cross',0x8dc2:'Arbalest',
0x8de0:'Crisscross',0x8dfa:'Cupid Bow',0x8e3e:'Paralysis Cross',0x8e4e:'Basilisk Cross',0x8e6a:'Soul Fly',
}
MAGIC={
'000014ea':('Sawgear','Sawgear'),
'00001870':('Steel Giant Mech','Steel Giant'),
'000018e4':('Dawn-Hope Great Mech','Dawn Great Mech'),
'00001960':('Sky Annihilation Mech','Sky Annihilator'),
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 idx=json.loads((ROOT/'work/translation/en/interface.index.json').read_text());rows={r['id']:r for t in idx['tables'] for r in t['strings']}
 wp=F/'weapon_review.targets.json';w=json.loads(wp.read_text())
 for off in (0x84a8,0x84b8,0x84c6,0x84e4,0x855a,0x8dd0):
  w['translations'].pop('02:00003/00015:ui:%08x'%off,None)
 w['excluded_with_notes']=['Six uncertain coined names omitted after independent meaning review.']
 for off,text in WEAPONS.items():
  identity='02:00003/00015:ui:%08x'%off;r=rows[identity]
  assert len(text)<=15
  w['translations'][identity]=dict(source_sha256=r['source_sha256'],text=text,compact=text,status='manual_source_reading')
 mp=F/'magic.targets.json';m=json.loads(mp.read_text())
 for off,(text,compact) in MAGIC.items():
  r=m['translations']['02:00003/00012:ui:'+off];r.update(text=text,compact=compact,review='Independent source meaning correction')
 m['translations']['02:00003/00012:ui:000019d6']['review']='Provisional descriptive interpretation; exact proper-name localization unconfirmed'
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',weapon_decisions=len(WEAPONS),magic_corrections=MAGIC,samples=list(w['translations'].items())[:3]),indent=2))
 if a.write:
  for path,data in [(wp,w),(mp,m)]:path.write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
