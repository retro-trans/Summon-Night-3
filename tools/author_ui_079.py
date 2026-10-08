"""Author UI category targets from locally resolved source; keep source scripts private."""
import hashlib,json,re,struct,unicodedata
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue
from menu_hotfix_017 import lines_at
from battle_elf_refs import references

F=ROOT/'work/translation/en/ui_0.1.79'
sha=lambda b:hashlib.sha256(b).hexdigest()
NAMES={24:'Flame Shot',29:'Water Shot',34:'Water Shot',39:'Wind Blade',44:'Wind Blade',49:'Ice Shot',54:'Ice Shot',59:'Lightning Shot',64:'Starlight Shot',69:'Dark Shot',74:'Rock Shot',79:'Acid Spit',84:'Flash Break',87:'Sage Release',90:'Flash Break',93:'Sage Release',96:'High Rush',99:'Needle Shot',102:'Paralyze Attack',105:'Delta Slash',108:'Deadly Strike',111:'True Deadly Blow',114:'Wild Fire',117:'Machine Volley',120:'Viper Blade',123:'Shadow Draw',126:'Phantom Sword',129:'Raging Tiger',132:'CSS Pierce',135:'Purgatorio',138:'V-Cannon',141:'Oni Storm Spear',144:'Thunder Axe',147:'Violet Flash',150:'Fangbreaker Fist',153:'Poison Needle',162:'Final Draw',165:'Briar Princess',168:'Resonant Combo',171:'Winged Combo',174:'Winged Combo',177:'Winged Combo',180:'Resonant Combo',183:'Winged Combo',186:'Winged Combo',189:'Winged Combo',192:'My Way Draw',195:'Warbreaker Bow',198:'Oni War Bow',201:'Thousand Peaks',204:'Lion Cleaver',207:'Tiger Palm',210:'Last Shot',213:'Dragon Combo',216:'Dragon Combo',219:'Moon Arcus',222:'Violet Spear',225:'Roaring Dragon',228:'Celestial Bow',231:'Quick Draw',234:'Tremor Draw',237:'Brave Attack',240:'Sector Bomb',243:'Sector Kick',246:'Grand Blaster',249:'Shadow Needle',252:'Blackwing Slash',255:'Lightning Pierce',258:'Oni Thunder Cut',261:'Maid Crisis',264:'Flamebreaker Axe',267:'Bloody Claw',270:'Skybreaker Spear',273:'Crimson Draw',276:'Binding Talisman',279:'Rizeld Buster',282:'Rata Cuerno',285:'Look!',288:'Ultimate Retort!',291:'Trick Edge',294:'Now I Am Mad!',297:'Shot Arrow',300:'Rain Shoot η',303:'Giga Break γ',306:'Volti Lance θ',309:"Sinner's Brand",310:'Lament Prison',311:'Existence Denial',312:'Betrayal Shards',313:'Hellfang Bite',314:'Gate of Rancor',315:'Satellite α',320:'Satellite β',325:'Maid Crisis',328:'Heat Rush',331:'Heart Break',334:'Stun Break',337:'Drei Schneid',340:'Lightning Shot',345:'Lightning Shot',350:'Dark Shot',355:'Lightning Shot',360:'Wind Blade',365:'Ice Shot',370:'Starlight Shot',375:'Flame Shot',380:'Dark Shot',385:'Look!',388:'Drunken Dragon',391:'Satellite Ω',394:'Briar Princess',397:'Skybound Release',400:'Skybound Release',403:'Rod Stunner',404:'Magic Attack',409:'Spirit Strike+',410:'Bite',411:'Bite',412:'Punch',413:'Punch',414:'Punch',415:'Punch',416:'Body Slam',417:'Body Slam',418:'Body Slam',419:'Body Slam',420:'Thrust',421:'Thrust',427:'Slash',428:'Shuriken',429:'Lick'}
AFF={'機':'Machine','鬼':'Yokai','霊':'Spirit','獣':'Beast','無':'Neutral'}
NAMES.update({102:'Paralyze',111:'True Deathblow',126:'Phantom Blade',141:'Oni Storm',150:'Fangbreaker',168:'Resonance',180:'Resonance',195:'Warbreaker',201:'Thousand Peaks',225:'Dragon Roar',249:'Shadow Needle',252:'Blackwing Cut',255:'Volt Pierce',258:'Oni Thunder',264:'Flamebreaker',270:'Skybreaker',276:'Binding Charm',288:'Grand Retort!',311:'Null Existence',312:'Betrayal',314:'Rancor Gate',388:'Drunk Dragon',397:'Sky Release',400:'Sky Release'})
WEAP={'短剣':'Dagger','大剣':'Greatsword','剣':'Sword','弓':'Bow','銃':'Gun','刀':'Katana','武具・爪':'Fist/Claw','武具':'Fist','爪':'Claw','ドリル':'Drill','槍':'Spear','斧':'Axe','投具':'Throw','杖':'Staff'}

def help_text(record,lines):
 t=' '.join(lines)
 aff=next((v for k,v in AFF.items() if k+'属性' in t),None)
 if '遠距離攻撃' in t:
  return [f'{aff} shot +12/Lv; MP up.']
 if record==79:return ['Spits Beast acid that', 'dissolves anything.']
 special={168:['Adjacent hit; guardian', 'must be nearby.'],171:['Adjacent hit; guardian','must be nearby.'],174:['Adjacent hit; guardian','must be nearby.'],177:['Adjacent hit; guardian','must be nearby.'],180:['Adjacent hit; guardian','must be nearby.'],183:['Adjacent hit; guardian','must be nearby.'],186:['Adjacent hit; guardian','must be nearby.'],189:['Adjacent hit; guardian','must be nearby.'],213:['Adjacent hit; dragon child','must be nearby.'],216:['Adjacent hit; dragon child','must be nearby.'],279:['Machine gun; infinite line','range, pierces all targets.'],285:['Distract for high damage.','Jakini original technique.'],385:['Distract for high damage.'],309:['Med. area physical hit.','May chain Prison same turn.'],310:["Med. area magic hit.","May chain Brand same turn."],311:['High area magic hit at set','time and location.'],312:['Indiscriminate map strikes;','each bolt hits one target.'],313:['Physical bite: enter area.','Windup before attack.'],314:['High magic: enter area.','Windup before attack.'],315:['Area: foes; leaders x0.5.'],320:['Area: foes; leaders x0.5.'],404:['Physical attack using MAT.'],409:['Physical damage split','equally between HP and MP.'],403:['Staff: adjacent hit +Para.']}
 if record in special:return special[record]
 if '射程:隣接マス' in t:return [f'Adjacent; up 2/down 2.',f'{aff} affinity.']
 weapon=next((v for k,v in WEAP.items() if k+'専用' in t),'')
 if '単体ビーム射撃' in t:area='Single target beam shot.'
 elif '縦3マス' in t:area='Pierces 3-square line.'
 elif '縦2マス' in t:area='Pierces 2-square line.'
 elif '小範囲' in t:area='Small area attack.'
 elif '中範囲' in t:area='Medium area; range 3.'
 elif '横一列3マス' in t:area='Hits 3-square row.'
 elif '周囲3マス' in t:area='Single hit; range 3.'
 elif '周囲2マス' in t:area='Single hit; range 2.'
 elif '弓射程範囲貫通' in t:area='Piercing hit in bow range.'
 elif '苦無投げ' in t:area='Single target kunai throw.'
 else:
  assert '隣接' in t,(record,t)
  area='Single adjacent hit.'
 details='; '.join(x for x in [weapon,aff] if x)
 if '状態異常' in t:
  effect=next((en for jp,en in [('毒','Poison'),('眠り','Sleep'),('マヒ','Para'),('召喚封じ','Summon Seal')] if '「'+jp+'」' in t),None)
  assert effect,(record,t)
  details += ('; ' if details else '')+'may '+effect
 return [area]+([details+'.'] if details else [])

def master_text(lines):
 t=' '.join(lines)
 for jp,en in AFF.items():
  if jp+'属耐性+5' in t:return [f'Master: {en} resist +5.']
 if '消費MP-15' in t:return ['Master: MP cost -15.']
 if 'マヒ' in t:return ['Master: may cause Para.']
 assert t.startswith('マスター効果:'),t
 return ['Master: '+t.split(':',1)[1]]

NATIVE={
0x216394:['Fariel'],0x2163a0:['Yes, everything looks fine.','Nya-ha-ha!♪'],
0x2163d0:['Up to something bad?','You should be careful.'],0x216414:['Are your friends hurt too?','Do not overdo it yourself.'],0x216458:['You are overdoing it.','Bad signs are appearing...'],0x216490:['Things are very dangerous.','But there is still hope.'],0x2164d4:['It may be too late...',' '],
0x2164f0:['It feels a little lonely...','I am rooting for you!'],0x216534:['Hmm...','Neither good nor bad.'],0x216560:['Oh!','There may be a spark here!'],0x216588:['Things look very good.','You could deepen this bond.'],0x2165c4:['What a lovely bond!','Meimei is getting jealous!'],0x216604:['You have come so far!','Lucky you, so loved!♪'],0x21664c:['A promising connection...','But bad signs interfere.'],0x21c6a4:['Fariel'],
0x217688:['Dagger'],0x217690:['Sword'],0x217694:['Greatsword'],0x21769c:['Axe'],0x2176a0:['Katana'],0x2176a4:['Staff'],0x2176a8:['Spear'],0x2176ac:['Throwing'],0x2176b4:['Bow'],0x2176b8:['Gun'],0x2176bc:['Fists'],0x2176c4:['Claws'],0x2176c8:['Drill'],0x2176d0:['Light Armor'],0x2176d8:['Heavy Armor'],0x2176e0:['Robe'],0x2176e8:['Kimono'],0x2176f0:['Beast Garb'],0x2176f8:['Plating'],
0x217708:['Adjacent: up 2/down 2.'],0x217728:['Adjacent: up 3/down 2.'],0x217748:['Adjacent: up 2/down 3.'],0x217768:['Adjacent: up 1/down 2.','Diagonal: up 0/down 1.'],0x2177a4:['Adjacent: up 4/down 3.','2nd square: up 3/down 2.'],0x2177e0:['Range 1-3; height varies.','Obstacles may block attack.'],0x217820:['Range 2-5; height varies.'],0x217848:['Range 1-5; height varies.','Obstacles may block attack.'],0x2179e8:['Adjacent: up 4/down 3.','2nd: up 3/down 2; pierces.'],0x217a2c:['Adjacent: up 3/down 3.']}

def main():
 F.mkdir(parents=True,exist_ok=True)
 src=json.loads((ROOT/'work/scratch/ui079-discovery/attacks.json').read_text('utf8'));entries=[]
 for e in src:
  slot=e['refs'][0]['slot'];rec=e['refs'][0]['record']
  en=[NAMES[rec]] if slot==8 else help_text(rec,e['text']) if slot==9 else master_text(e['text'])
  assert max(map(len,en))<= (16 if slot==8 else 29),(rec,slot,en)
  assert sum(map(len,en))<=54,(rec,slot,en)
  entries.append(dict(table=25,records=sorted(set(r['record'] for r in e['refs'])),slot=slot,pointer_fields=[r['pointer_field_offset'] for r in e['refs']],source_offset=e['ptr'],english=en))
 # Bind hashes to actual live strings, not normalized private reference text.
 from sn3_archive import GameSource,parse_index,child
 with GameSource(ROOT/'work/output/0.1.78/Summon_Night_3_EN_0.1.78.iso') as s:
  st=s.resource('02.DAT',3);b=child(st,parse_index(st,len(st)),25)
  for e in entries:
   raw=lines_at(b,e['source_offset'])[0];raw=raw[:1] if e['slot']==8 else raw
   e['source_sha256']=sha(b'\0\0'.join(raw))
 elf=(ROOT/'work/output/0.1.78/EBOOT.elf').read_bytes();refs=references(elf)[0];menus=[]
 for va,en in NATIVE.items():
  n=1 if va in (0x216394,0x21c6a4) or 0x217688<=va<=0x2176f8 else len(en)
  raw=lines_at(elf,va+192)[0][:n]
  assert len(raw)==n and sum(map(len,en))<=54 and max(map(len,en))<=27,(hex(va),en)
  menus.append(dict(source_address=va,source_lines=n,source_sha256=sha(b'\0\0'.join(raw)),english=en,bindings=refs[va]))
 (F/'targets.json').write_text(json.dumps(dict(version='0.1.79',source_build='0.1.78',entries=entries,menus=menus,category_scope=['All remaining attack-skill names/descriptions/master effects','All fortune evaluations and special Fariel labels','All equipment types and range descriptions'],numeric_fields_unchanged=True),indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(attack_fields=len(entries),native_groups=len(menus))))

if __name__=='__main__':main()


