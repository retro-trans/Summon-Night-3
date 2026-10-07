"""Create English UI targets from the immutable 073 tables; no source scripts."""
import hashlib,json,struct
from sn3_archive import ROOT,GameSource,parse_index,child
from character_labels import collect
from menu_hotfix_017 import lines_at
from battle_elf_refs import references

BASE=ROOT/'work/output/0.1.73'
DEST=ROOT/'work/translation/en/menus_0.1.74/targets.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
PARTY=[
 ('Pirate Lunch',['Gain 1 Pirate Lunch.','Event battles only.']),
 ('Homemade Lunch',['Gain 1 Homemade Lunch.','Event battles only.']),
 ('Battle Analysis',['View the level range','of the next battle.']),
 ('Safe Summoning',['Failed crafting may heal','instead of causing damage.']),
 ('Stone Search',['Win: +1 Summonite Stone.','Excludes retreats.']),
 ('Slot Hunter',['Slow the treasure chest','roulette.']),
 ('Treasure Hunt',['Extra item on event wins.','Excludes battle replays.']),
 ('Reckless Anthem',['Stronger foes; same rewards','Unavailable on Easy.']),
 ('Battle Council',['All allies: physical','critical chance +10%.']),
 ('Focus',['All allies: physical','accuracy +10%.']),
 ('Sixth Sense',['All allies: physical','evasion +10%.']),
 ('Potent Items',['Battle healing items +20%.','Excludes food.']),
 ('Big Eater',['Each unit can eat 3 foods','per battle.']),
 ('Big Eater 2',['Each unit can eat 4 foods','per battle.']),
 ('Big Eater 3',['Each unit can eat 5 foods','per battle.']),
 ('All-Purpose Bag',['Craft summons using','unequipped key items.']),
 ('Quiet Support',['Summon Assist: MP cost -5','for assisting units.']),
 ('Lucky Charm',['More gift units in Free','Battle and Endless Halls.']),
 ('Neutral Ward',['All allies take less damage','from Neutral summon magic.']),
 ('Right Role',['Skill MP cost -10%.']),
 ('Warm-Up',['Deployed allies: HP +10%.','Base only; no gear/skills.']),
 ('Brief Meditation',['Base max MP +10%.','Excludes skill/gear boosts.']),
 ('Caution',['All allies take less','counterattack damage.']),
 ('World Knowledge',['All allies: every','affinity resistance +5.']),
 ('Training',['Gain 1 extra Skill Point','on each level up.']),
 ('Hero Tales Vol.1',['EXP gained +50%.']),
 ('First Aid',['All allies: recover 5 HP','each player turn.']),
 ('Mutual Support',['All allies: recover 5 MP','each player turn.']),
 ('Moonflower Grace',['Support abilities activate','more often.']),
]
CLASSES=['Marurur','Flower Fairy','Cupid','Precocious Fairy','Smiling Hero','Fairy Princess','Fluffy Sage']
PARTY_COMPACT={'Homemade Lunch':'Home Lunch','Battle Analysis':'Battle Intel',
 'Safe Summoning':'Safe Summon','Reckless Anthem':'Reckless Song',
 'All-Purpose Bag':'Craft Bag','Brief Meditation':'Meditation',
 'World Knowledge':'World Lore','Hero Tales Vol.1':'Hero Tales 1',
 'Moonflower Grace':'Moonflower'}
HERO_MENUS=[(0x216100+i*16,'Hero Tales '+str(i+1)) for i in range(5)]+list(zip(
 [0x21615c,0x216178,0x216190,0x2161ac,0x2161c4,0x2161dc],
 ['EXP gained x1.5.','EXP gained x2.','EXP gained x2.5.',
  'EXP gained x3.','EXP gained x4.','EXP gained -100%.']))

def main():
 assert not DEST.exists()
 entries=[];labels=[];menus=[]
 with GameSource(BASE/'Summon_Night_3_EN_0.1.73.iso') as source:
  static=source.resource('02.DAT',3);si=parse_index(static,len(static));tb=child(static,si,37)
  assert struct.unpack_from('<I',tb)[0]==30
  for record,(name,help_lines) in enumerate(PARTY,1):
   for slot,english in [(1,[PARTY_COMPACT.get(name,name)]),(2,help_lines)]:
    fields=[4+record*12+slot*4];p=struct.unpack_from('<I',tb,fields[0])[0]
    raw=lines_at(tb,p)[0];raw=raw[:1] if slot==1 else raw
    entries.append(dict(table=37,records=[record],slot=slot,source_offset=p,source_sha256=sha(b'\0\0'.join(raw)),pointer_fields=fields,english=english,kind='name' if slot==1 else 'help'))
    if slot==1 and name in PARTY_COMPACT:entries[-1]['full_translation']=name
  # Item-menu food help is a separate category from the Cooking book text.
  food=[['Food: HP +50.'],['Food: HP +80.'],['Food: HP +25; cure Poison.'],
        ['Food: HP +30; cure Sleep.'],['Food: HP +40.','Cure Paralysis.'],
        ['Food: HP +55.','Cure Petrify and Poison.'],['Food: HP +70.','Cure Paralysis and Blind.'],
        ['Food: MP +20; cure Sleep.'],['Food: HP +85.','Cure Summon Seal.'],
        ['Food: HP +135; cure Charm.'],['Food: HP +100; cure Poison,','Paralysis and Sleep.'],
        ['Food: MP +40.','Cure Charm and Berserk.'],['Food: HP +280.'],
        ['Food: HP +170; cure Petrify','Berserk/Blind/Summon Seal.'],
        ['Food: HP +75.','Cure all status ailments.']]
  tb=child(static,si,19)
  for record in list(range(60,75))+list(range(110,124)):
   english=food[record-60] if record<75 else (['Boosts summons of','any affinity.'] if record<112 else [f'Boosts {dict(zip(range(112,124),["Mech"]*3+["Oni"]*3+["Spirit"]*3+["Beast"]*3))[record]} summons.','Humans cannot eat this.'])
   fields=[4+record*24+20];p=struct.unpack_from('<I',tb,fields[0])[0];raw=lines_at(tb,p)[0]
   entries.append(dict(table=19,records=[record],slot=5,source_offset=p,source_sha256=sha(b'\0\0'.join(raw)),pointer_fields=fields,english=english,kind='help'))
  data,_,strings=collect(source)
  for slot,target in enumerate(CLASSES,1):
   e=next(e for e in strings if any(r['row']==115 and r['slot']==slot for r in e['references']))
   labels.append(dict(e,english=[target]))
  # The alternate Moonflower class appears in the same status-name category.
  e=next(e for e in strings if e['source_offset']==30720)
  labels.append(dict(e,english=['Moonflower Fairy'],full_translation='Moonflower Fairy Princess'))
 elf=(BASE/'EBOOT.elf').read_bytes();refs=references(elf)[0]
 for va,target in [(0x21625c,'Deploy using Unit Summon.'),(0x21e1e0,'Main Story'),(0x21e1ec,'Extra Story')]+HERO_MENUS:
  raw=lines_at(elf,va+192)[0][:1]
  menus.append(dict(source_address=va,source_lines=1,source_sha256=sha(raw[0]),english=[target],bindings=refs[va]))
 # Three branch delay slots feed the shared low instruction. The linear
 # reference scanner cannot infer these alternate control-flow edges.
 va=0x21629c;raw=lines_at(elf,va+192)[0][:1]
 menus.append(dict(source_address=va,source_lines=1,source_sha256=sha(raw[0]),english=['Deploy using Unit Summon.'],
  bindings=[dict(kind='hilo',high=hi,low=0x5d534,register=4) for hi in (0x5d508,0x5d510,0x5d520)],branch_delay_references=True))
 DEST.parent.mkdir(parents=True,exist_ok=True)
 DEST.write_text(json.dumps(dict(schema_version=1,version='0.1.74',entries=entries,labels=labels,menus=menus),indent=2)+'\n')
 print(json.dumps(dict(party_fields=len(entries),unit_labels=len(labels),native_texts=len(menus))))

if __name__=='__main__':main()
