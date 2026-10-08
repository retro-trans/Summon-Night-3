"""Author bounded Replay conditions and remaining native UI categories on 079."""
import json,struct,textwrap,unicodedata,hashlib
from sn3_archive import ROOT,GameSource,parse_index,child
from spell_name_059 import label
from menu_hotfix_017 import lines_at
from battle_elf_refs import references
from dialogue_encoding import encode_dialogue
from stat_spacing_026 import _file_offset_for_va as file_offset

DEST=ROOT/'work/translation/en/ui_0.1.80'
NAMES={11:'Poison a foe with an obstacle.',0:'Sonolar/Scarrel stay healthy.',1:'Kyle and Yard stay healthy.',3:'KO a foe with an obstacle blast.',5:'Poison a foe with an obstacle.',7:'Petrify a foe with an obstacle.',9:'KO a foe with an obstacle blast.',14:'A pupil KOs Galleor or Vijue.',16:'No ally becomes critical.',17:'KO Queen before attack 12.',18:'Defeat Azlier before Preempt.',19:'Clear without Blade Awakening.',21:'KO Azlier & Galleor in one turn.',22:'Clear without status ailments.',24:'Clear without status ailments.',26:'Defeat Jakiini while afflicted.',27:'Every deployed ally KOs a foe.',28:'No enemy possession.',29:'Protagonist defeats Ishlar.',31:'Defeat Azlier last.',32:'Friend summon: E+ magic 3 times.',34:'Protagonist KOs Azlier & Ishlar.',36:'Azlier & Galleor: 5+ KOs total.',37:'Defeat 3+ afflicted foes.',42:'KO 2+ main fighters in one turn.',43:'Defeat Hazel last.',44:'KO leader with 5+ unit assist.',46:'No enemy uses Berserk Summon.',48:'Blast 2+ foes with an obstacle.',49:'KO Cunnon with Machine magic.',51:'Jakiini: 3 special attacks.',52:'Defeat all foes with magic.',53:'No enemy possession.',54:'KO a foe with an obstacle blast.',56:'Clear by defeating only Marurur.',58:'Clear without status ailments.',59:'Afflict 4+ foes with ailments.',60:'No enemy uses Berserk Summon.',61:'KO a foe with an obstacle blast.'}
HELP={11:['Poison 1+ foes with an','obstacle.'],
0:['Sonolar/Scarrel: avoid','critical HP or being KOed.'],1:['Kyle/Yard: no critical HP','or incapacitation.'],
3:['KO 1+ foes with an','obstacle explosion.'],5:['Poison 1+ foes with an','obstacle.'],7:['Petrify 1+ foes with an','obstacle.'],9:['KO 1+ foes with an','obstacle explosion.'],
14:['A pupil defeats either','Galleor or Vijue.'],16:['No deployed ally reaches','critical HP or is KOed.'],17:['Defeat Queen Jilcooda','before her 12th attack.'],18:['Defeat Azlier before her','Preempt stance activates.'],19:['No voluntary or automatic','Blade Awakening.'],21:['Defeat Azlier and Galleor','in the same turn.'],
22:['Petrify/Poison/Para/Blind','Charm/Sleep/Seal/Berserk'],24:['Petrify/Poison/Para/Blind','Charm/Sleep/Seal/Berserk'],26:['Defeat Jakiini while he has','any status ailment.'],27:['Every deployed ally KOs 1+.','Summoned units excluded.'],28:['No unit may be possessed','by enemy possession magic.'],29:['The protagonist must','defeat Ishlar.'],31:['Defeat Azlier last.'],32:['Use a friend summon\'s magic','rank E+ at least 3 times.'],34:['The protagonist defeats','both Azlier and Ishlar.'],36:['Azlier and Galleor defeat','5+ enemies between them.'],37:['Defeat 3+ foes with any','status ailment.'],42:['Defeat 2+ of Ishlar, Vijue','and Hazel in the same turn.'],43:['Defeat Hazel last.'],44:['KO Ordreik with a Summon','Assist of 5+ participants.'],46:['No enemy may use','Berserk Summon.'],48:['Damage 2+ foes with an','obstacle explosion.'],49:['Defeat Cunnon with Machine','affinity summon magic.'],51:['Jakiini uses a special','attack 3 times.'],52:['Defeat all foes with','summon-magic damage.'],53:['No unit may be possessed','by enemy possession magic.'],54:['KO 1+ foes with an','obstacle explosion.'],56:['Clear after defeating','only Marurur.'],58:['Petrify/Poison/Para/Blind','Charm/Sleep/Seal/Berserk'],59:['Inflict any status ailment','on at least 4 enemies.'],60:['No enemy may use','Berserk Summon.'],61:['KO 1+ foes with an','obstacle explosion.']}
CHAPTERS={0x21cc14:'Ch. 1',0x21cc30:'Ch. 2',0x21cc4c:'Ch. 3',0x21cc6c:'Ch. 4',0x21cc8c:'Ch. 5',0x21cca8:'Ch. 6',0x21ccc4:'Ch. 7',0x21cce0:'Ch. 8',0x21ccf4:'Ch. 9',0x21cd0c:'Ch. 10',0x21cd28:'Ch. 11',0x21cd40:'Ch. 12',0x21cd5c:'Ch. 13',0x21cd74:'Ch. 14',0x21cd90:'Ch. 15',0x21cdac:'Ch. 16',0x21cdc8:'Final',0x21cde4:'Ending',0x21ce08:'Extra',0x21ce28:'Ch. 9S',0x21ce48:'Ch. 10S',0x21ce64:'Ch. 11S',0x21ce80:'Ch. 12S',0x21cea0:'Clear Data'}
PROF={0x35badc:'Cntr+',0x35bb00:'Wpn ailment+',0x35bb32:'Ailment+',0x35bb56:'M: Rare CR KO',0x35bb8e:'M: Foe cntr down',0x35bbc8:'M: Pierce 2 tiles',0x35bbfc:'M: Hit height +/-1',0x35bc30:'M: Snipe',0x35bc56:'M: Half range penalty'}
MASTERS={26:'M: Rare CR KO',31:'M: Foe cntr down',36:'M: ━ 5',41:'M: Foe cntr down',46:'M: ━ 10',51:'M: evade +15%',56:'M: Pierce 2 tiles',61:'M: evade+15% cntr+10%',66:'M: ailment odds up',71:'M: Hit height +/-1',76:'M: Snipe',81:'M: Half range penalty',86:'M: Snipe'}
TITLES={0x21cc20:'A Sudden Beginning',0x21cc3c:'Cheerful Castaways',0x21cc58:'Island of Outcasts',0x21cc78:'A Troublemaker from the Sea',0x21cc98:'A Place to Belong',0x21ccb4:'Uninvited Visitors',0x21ccd0:'Hearts at Cross-Purposes',0x21ccec:'Coward',0x21cd00:"A Teacher's Day Off",0x21cd18:'Entangled Truths',0x21cd34:'The Afterglow of Days Gone By',0x21cd4c:'Twilight Descends',0x21cd68:'The Sword of Judgment',0x21cd80:'Things Fall Apart',0x21cd9c:'One Answer',0x21cdb8:'What He Wished For',0x21cdd4:'At the Edge of Paradise',0x21cdf8:'The Price of a Smile',0x21ce14:'Heirs to Paradise',0x21ce38:'The Erratic Pendulum',0x21ce58:'Mother and Child',0x21ce74:'Where the Soul Goes',0x21ce90:'An Endless Vow'}

def main():
 DEST.mkdir(parents=True,exist_ok=True)
 base=ROOT/'work/output/0.1.79';elf=(base/'EBOOT.elf').read_bytes();refs,_,_=references(elf)
 entries=[]
 with GameSource(base/'Summon_Night_3_EN_0.1.79.iso') as s:
  st=s.resource('02.DAT',3);ix=parse_index(st,len(st));b=child(st,ix,46)
  for r in range(62):
   for slot in range(7,17):
    f=4+r*68+slot*4;p=struct.unpack_from('<I',b,f)[0]
    if not p:continue
    old=label(b,f);raw=lines_at(b,p)[0][0]
    if slot==7:ls=[NAMES.get(r,old)]
    elif slot==8:ls=HELP.get(r,textwrap.wrap(old,27,break_long_words=False,break_on_hyphens=False))
    else:
     # Alternate guardian names and their corresponding help occupy slots 9..16.
     name=['R','Onibi','Quiupy','Teco'][(slot-9)%4]
     ls=[f'{name}: E+ magic 3 times.'] if slot<=12 else [f'Use {name}\'s magic of rank','E+ at least 3 times.']
    # Apply the current identity spellings to these new inputs only.
    for old,new in [('Galleor','Galeor'),('Jakiini','Jakini'),('Cunnon','Kunon'),('Tselline','Zeline'),('Wizel','Vizel'),('Oukini','Ohkini')]:
     ls=[t.replace(old,new) for t in ls]
    if slot in (7,9,10,11,12):assert len(ls)==1 and len(ls[0])<=32,(r,slot,ls)
    else:assert len(ls)<=3 and max(map(len,ls))<=27 and sum(map(len,ls))<=54,(r,slot,ls)
    entries.append(dict(table=46,record=r,slot=slot,field=f,source_offset=p,source_sha256=hashlib.sha256(raw).hexdigest(),english=ls))
  b=child(st,ix,34)
  for r,t in MASTERS.items():
   f=4+r*48+40;p=struct.unpack_from('<I',b,f)[0];raw=lines_at(b,p)[0][0]
   entries.append(dict(table=34,record=r,slot=10,field=f,source_offset=p,source_sha256=hashlib.sha256(raw).hexdigest(),english=[t]))
 native=[]
 for va,ls in {**{v:[t] for v,t in {**CHAPTERS,**TITLES}.items()},0x21e208:['Select a battle.','АSelect ВBattle info'],0x21e238:['"'],0x21e240:['"'],0x21debc:['Not enough Skill Points.'],0x21dedc:['This skill is maxed out.'],0x21df44:['Unknown'],0x21dee8:['Unknown']}.items():
  if va in (0x21e240,):continue
  raw=lines_at(elf,va+192)[0][:len(ls)]
  native.append(dict(source_address=va,source_lines=len(raw),source_sha256=hashlib.sha256(b'\0\0'.join(raw)).hexdigest(),english=ls,bindings=refs.get(va,[])))
 for va,t in PROF.items():
  raw=lines_at(elf,file_offset(elf,va))[0][:1]
  native.append(dict(source_address=va,source_lines=1,source_sha256=hashlib.sha256(raw[0]).hexdigest(),english=[t],bindings=refs[va]))
 cfg=dict(version='0.1.80',base='0.1.79',entries=entries,menus=native,popup_vwf_names=['This skill is maxed out.','Cannot raise this level.','Cannot learn this.','Required class not unlocked.','Not enough Skill Points.'],scope=['All battle-specific Brave Order names and help, including guardian alternatives','All chapter labels and titles used by Replay and saves','Learn Skills failure notifications','All summon default names on popup and battle banner widgets'])
 (DEST/'targets.json').write_text(json.dumps(cfg,indent=2)+'\n')
 print(json.dumps(dict(table_fields=len(entries),native_groups=len(native))))
if __name__=='__main__':main()




