"""Author compact English gallery categories and safe native menu descriptions."""
import json,struct,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from menu_hotfix_017 import lines_at
from battle_elf_refs import references
from stat_spacing_026 import _file_offset_for_va
F=ROOT/'work/translation/en/menus_0.1.76'
G=ROOT/'work/ui/menus_0.1.76'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 F.mkdir(parents=True,exist_ok=True);(G/'generated').mkdir(parents=True,exist_ok=True)
 titles=json.loads((ROOT/'work/scratch/menus076-discovery/titles.json').read_text())
 groups=[
 (0,'Title|Movement|Direction and Height|Range and Weapons|Stances|Status Ailments|Obstacles|Skills|Summon Magic|Create Summons|Affinity Resistance|Summon Assist|Favorite Summons|Blade Awakening|Brave Battles|Party Abilities|Event Battle Replay|Cooking|Train Summoned Units|Level Drain|Materialize Puppets|Karma'),
 (25,'Title|Lyndbaum: The Other World|Summoning and Summons|Machine World: Loreilal|Yokai World: Silturn|Spirit World: Sapureth|Beast World: Maetropa|The Forgotten Island|Latrikss|Wind and Thunder Village|The Realm Between|Yucres Village|Gathering Spring|Evocation Gate|The Empire|Pirates|The Colorless Faction|Red Gloves|Sealed Sword|The Summoning Curse|Demon Sword and Smith|Core Cognizance and Boundary|Dielgo|Primal Sin'),
 (49,'Title|Rexx|Rexx: Blade Awakening|Aty|Aty: Blade Awakening|Nup|Belfraw|Alieze|Will|Ardylia|Kyuuma|Falzen|Fariel|Yafha|Kyle|Sonolar|Scarrel|Yard|Kunon|Var-Xe-LD|Misumi|Subaru|Phlaiz|Marurur|Islanders|Jakini\'s Crew|Azlier|Galeor|Vijue|Ishlar|Ishlar: Blade Awakening|The Colorless Faction|Colorless Allies|Meimei'),
 (83,'Title|Rexx: Full Body|Rexx: Expressions|Aty: Full Body|Aty: Expressions|Nup: Full Body|Nup: Expressions|Belfraw: Full Body|Belfraw: Expressions|Alieze: Full Body|Alieze: Expressions|Will: Full Body|Will: Expressions|Rexx|Aty|Nup|Belfraw|Alieze|Will|Ardylia and Kunon|Kyuuma|Falzen|Yafha and Marurur|Kyle and Sonolar|Scarrel|Yard|Misumi and Subaru|Phlaiz'),
 (124,'Title'),(140,'Title|Protagonist!|Main Visual|Package|Teacher and Students|Nup and Will|Alieze and Bell|Two Teachers|Little Extras|Playing the Extra Story|Group Photo!'),
 (151,'Title|Blade Awakening!|Blue Sky School|When I Woke Up...|Azlier Collapses|Meimei Appears|Ishlar: Blade Awakening|Saver vs. Reaver|The Shape of Memories|The Lawlers|Undying Flame|What We Inherit|Unbeatable Smile|By Your Side|With Honest Feelings|Paradise Close at Hand|At Eye Level|Embraced by Peace|Sighs and Smiles|Toward Unseen Seas|Sunny Again Tomorrow!|The Sun and the Snake|A New Teacher|A Mechanical New Student|Go with the Flow|Eyes Full of Dreams|Wishing You Happiness|Keep on Smiling!|Memories Become Strength|From Here to Eternity|The Price of a Smile|I Am Happy')]
 gallery={start+i:t for start,text in groups for i,t in enumerate(text.split('|'))}
 gallery.update({111+i:f'Opening Scene {i+1}' for i in range(13)})
 gallery.update({125+i:f'Summon Concept Art {i+1}' for i in range(12)})
 gallery.update({137+i:f'Bonus Image {i+1}' for i in range(3)})
 music='Lyndbaum / Utopia|Together: From a Distant Island|A Day at Sea|To the You I Imagined|Days of New Adventures|An Island Stroll|A Mechanical Friend|Kin of Wind and Thunder|Guidance of the Wise|A Cheerful Visitor|Drawn by the Sun|A Merry Feast|Dark Curse: It\'s Us!|Tipsy Days|Pride of the Imperial Army|Unyielding Patriots|A Clear Mind|March of the Mighty|Birth of a Hero|A Heart Reflected on Water|Ruffling Wings|Unease|Hour of Calamity|A Blade Through the Void|Holding Back Feelings|Gently Unraveled|Lion King / Demon King\'s Stir|Colors of Change|FIGHT WITH BRAVE|Ergo\'s Madness / World Enemy|Together: Distant Island (2)|Embracing It All (1)|Embracing It All (2)|Forever From Now On|Together with You (SN2)|Her Sunshine (SN2)|Cast Off the Darkness (SN2)|Battle of Heroes (SN2)'.split('|')
 assert len(music)==38
 entries=[]
 with GameSource(ROOT/'work/output/0.1.75/Summon_Night_3_EN_0.1.75.iso') as s:
  b=s.resource('02.DAT',3);ix=parse_index(b,len(b));mappings={}
  for n,values in [(38,gallery),(39,dict(enumerate(music)))]:
   data=child(b,ix,n)
   for e in titles[str(n)]:
    if not e['text']:continue
    text=values[e['row']];assert len(text)<=32
    ptr=struct.unpack_from('<I',data,e['field'])[0];raw=lines_at(data,ptr)[0][0]
    entries.append(dict(table=n,row=e['row'],pointer_fields=[e['field']],source_offset=ptr,source_sha256=sha(raw),english=[text],kind='name'))
    if n==38:mappings[e['text'].encode('cp932')]=text
  # Gallery menu metadata contains the same titles in a separate resident table.
  data=child(b,ix,19)
  for row in range(struct.unpack_from('<I',data)[0]):
   f=4+row*24;p=struct.unpack_from('<I',data,f)[0]
   raw=lines_at(data,p)[0][0]
   if raw not in mappings:continue
   entries.append(dict(table=19,row=row,pointer_fields=[f],source_offset=p,source_sha256=sha(raw),english=[mappings[raw]],kind='name'))
 (F/'titles.json').write_text(json.dumps(dict(version='0.1.76',entries=entries),indent=2)+'\n')
 elf=(ROOT/'work/output/0.1.75/EBOOT.elf').read_bytes();refs=references(elf)[0]
 native={0x33e4e4:['Adjust music volume.'],0x33e514:['Enable event voices.'],0x33e554:['Show damage forecasts.'],0x33e594:['Set battle cursor','directions.'],0x33e5d4:['Set L/R controls in battle.'],
  2225880:['Image'],2225892:['Event','Back'],2225908:['Back'],2226100:['Move'],2226108:['Zoom'],2226116:['Rotate'],2226124:['Prev'],2226136:['Next'],2226148:['Hide'],2226208:['Confirm'],2226216:['Back'],2226224:['Character']}
 native[0x216f7c]=['Try on and buy equipment.','No items are sold here.']
 rows=[]
 for va,english in native.items():
  source_lines=1 if va==0x216f7c else len(english)
  raw=lines_at(elf,_file_offset_for_va(elf,va))[0][:source_lines]
  assert len(raw)==source_lines;assert all(len(t)<=27 for t in english)
  rows.append(dict(source_address=va,source_lines=len(raw),source_sha256=sha(b'\0\0'.join(raw)),english=english,bindings=refs[va]))
 (F/'native.json').write_text(json.dumps(dict(entries=rows),indent=2)+'\n')
 print(len(entries),len(rows))
if __name__=='__main__':main()
