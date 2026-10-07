"""English UI graphic targets; native source remains in the local game image."""
import json
from sn3_archive import ROOT
MAPS={37:['Island Map','My Room',"Teacher's Room",'Bridge',"Sonolar's Room","Scarrel's Room","Yard's Room",'Bow Deck','Stern Deck','Outside Ship','Mast','Warehouse'],
45:['Island Map','Central Control','Repair Center','Supply Dock','Power Facility','Signal Tower','Scrap Heap','Sub Street'],
53:['Island Map','Oni Palace','Garden','Guardian Shrine','Well Square',"Genji's Hut",'Field','Great Lotus Pond'],
61:['Island Map','Meditation Shrine','Mirror Pool','Chanting Square','Crystal Plateau','Illusion Forest','Twin Crystals'],
69:['Island Map',"Slacker's Hut",'Fairy Flower Garden','Yucres Square','Wishing Tree','Fruit Orchard','Potato Field'],
77:['Pirate Ship','Machine Village','Oni Village','Spirit Village','Beast Village',"Meimei's Shop",'Starting Beach','Forest','Rocky Shore','Hideout Edge','Gathering Spring','Open-Air School','Forest',"Jakini's Hideout",'Dragonbone Fault','Dawn Hill','Abandoned Mine','Evocation Gate','Ruins Entrance','Dusk Gravestone','Hills and Ruins','Forest 2']}
SHOP={37:'Materialize',43:'Try Your Luck',45:'Fortune',47:'Summons',49:'Favorites',51:'Rename',53:'Trials',55:'Replay',57:'Endless Halls',59:'Rebirth',61:'Shop',75:'Darts',77:'Scratch Cards',79:"Meimei's Shop"}
def main():
 entries=[]
 for root,names in MAPS.items():
  for n,text in enumerate(names):entries.append(dict(bank='02.DAT',path=[root,4],sprite=n,text=text,kind='map'))
 for n,text in enumerate(['Oni Village','Island Map','Pirate Ship','Machine Village','Spirit Village','Beast Village']):
  if n!=1:entries.append(dict(bank='02.DAT',path=[35,33],sprite=n,text=text,kind='heading'))
 for n,text in SHOP.items():
  for state in [n,n+1]:entries.append(dict(bank='02.DAT',path=[1338,10,state],sprite=0,text=text,kind='shop',state='selected' if state==n else 'unselected'))
 # Shared shop states absent from the Meimei pack.
 for root,child,n,text in [(1339,10,21,'Try On'),(1339,10,22,'Try On'),(1339,10,24,'Buy'),(1339,10,26,'Sell'),(1353,5,33,'Level Up'),(1353,5,34,'Level Up')]:
  entries.append(dict(bank='02.DAT',path=[root,child,n],sprite=0,text=text,kind='shop'))
 for n,text in enumerate(MAPS[77]):entries.append(dict(bank='02.DAT',path=[84,4],sprite=n,text=text,kind='map'))
 dest=ROOT/'work/translation/en/menus_0.1.75/graphics.json';dest.parent.mkdir(exist_ok=True)
 dest.write_text(json.dumps(dict(version='0.1.75',entries=entries),indent=2)+'\n',encoding='utf8')
 # Atlas needs one tile per visible English label; repeated states share art.
 labels=list(dict.fromkeys(e['text'] for e in entries))
 batches=[labels[i:i+24] for i in range(0,len(labels),24)]
 (ROOT/'work/scratch/menus075-atlas-labels.json').write_text(json.dumps(batches),encoding='utf8')
 print(len(entries),len(labels))
if __name__=='__main__':main()

