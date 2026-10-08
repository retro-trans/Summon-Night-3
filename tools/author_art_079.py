"""Versioned location entry graphics category with English-only metadata."""
import json
from sn3_archive import ROOT,GameSource
from menu_art_075 import descend,sha
LABELS={124:'Starting Beach',125:'Imperial Port: Adneas',126:'Guest Room',127:'Deck',128:'Ship Corridor',129:'Pirate Ship',137:'Rocky Shore',138:'Rocky Reef',139:'Near the Hideout',142:"Meimei's Shop",143:"Jakini's Hideout",145:'Grove',146:'Forest',149:'Dawn Hill',155:'Gathering Spring',159:'Open-Air School',160:'Ruins',161:'Reef Cliffs',162:'Dragonbone Fault',163:'Dusk Gravestone',166:'Evocation Gate',167:'Before the Ruins',168:'Ruins: Gate of the Humble',169:'Ruins: Gate of Cognizance',170:'Ruins: Chamber of Deep Lore',171:'Ruins: Chamber of Precepts',172:'Ruins: Chamber of Core Cognizance',175:"Isuadora's Warm Sea",178:'Azure Falls',195:'Hideout: Pirate Ship',196:"Captain's Room",199:'My Room',201:"Student's Room",203:"Sonolar's Room",204:"Scarrel's Room",205:"Yard's Room",208:'Warehouse',209:'Bow Deck',211:'Stern Deck',213:'Outside Ship',225:'Machine Village: Latrix',227:'Steel Bridge',229:'Central Control',230:'Repair Center',231:'Treatment Room',232:'Supply Dock',233:'Power Facility',234:'Signal Tower',235:'Scrap Heap',237:'Sub Street',245:'Oni Village: Wind and Thunder',247:'Rainy Lane',250:'Oni Palace',251:'Guardian Shrine',252:'Well Square',253:"Genji's Hut",254:'Great Lotus Pond',255:'Field',265:'Spirit Village: In Between',267:'Illusion Forest',269:'Meditation Shrine',270:'Otherworld Spring',271:'Chanting Square',272:'Crystal Plateau',273:'Twin Crystals',285:'Beast Village: Yucres',287:'Treetop Village',289:"Slacker's Hut",290:'Fairy Flower Garden',291:'Yucres Square',292:'Wishing Tree',293:'Fruit Orchard',294:'Potato Field',295:'Ancient Tree House',306:'Yucres Village',307:'Imperial Territory: Basiris',308:'Northern Harune: Pirate Ship',309:'Starfall Hill',327:'Pleasure Ship: Onboard',329:'Ship Cabin',330:'Ruins: Forbidden Domain',331:'Seat of Core Cognizance'}
def main():
 f=ROOT/'work/ui/ui_0.1.79';f.mkdir(parents=True,exist_ok=True)
 old=json.loads((ROOT/'work/ui/menus_0.1.75/atlas_spec.json').read_text());existing=set(sum(old['labels'],[])+old['corrections'])
 missing=sorted(set(LABELS.values())-existing);batches=[missing[i:i+20] for i in range(0,len(missing),20)]
 entries=[]
 with GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as s:
  for root,text in LABELS.items():
   path=[root,1];b=descend(s.resource('02.DAT',root),[1]);entries.append(dict(bank='02.DAT',path=path,sprite=0,text=text,kind='location_entry',source_sha256=sha(b)))
 (ROOT/'work/translation/en/ui_0.1.79/graphics.json').write_text(json.dumps(dict(version='0.1.79',entries=entries),indent=2)+'\n')
 (f/'atlas_spec.json').write_text(json.dumps(dict(version='0.1.79',labels=batches,reuse_atlas='work/ui/menus_0.1.75/atlas_spec.json'),indent=2)+'\n')
 print(json.dumps(batches,indent=2))
if __name__=='__main__':main()

