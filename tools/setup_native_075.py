"""Author the remaining equipment, reward, and Meimei native UI families."""
import json,hashlib
from sn3_archive import ROOT
from menu_hotfix_017 import lines_at
from battle_elf_refs import references
from dialogue_encoding import encode_dialogue
TEXTS={
0x21515c:['Meimei'],0x2160e8:['Rexx'],0x216234:['Aty'],0x21623c:['Magna'],0x216244:['Toris'],
0x2162d8:['Dismiss'],0x2162e0:['Dismiss a summon.'],0x216308:['Remove an obstacle.'],
0x218a44:['Nothing equipped.'],0x218a60:['Same weapon equipped.'],0x218b24:['Nothing held.'],0x218b40:['Out of stock.'],0x218b60:['Closed.'],
0x218be8:['Already registered.'],0x218bfc:['Not enough points.'],0x218c1c:['You do not own this summon.'],0x218c40:['Cannot change this name.'],0x218c68:['Cannot lower this level.'],0x218c8c:['Cannot lower it further.'],0x218cac:['Cannot eat this food.'],0x218ccc:['Cannot eat any more.'],0x218cec:['No favorite summon set.'],0x218d14:['Already a favorite.'],0x218d34:['Not enough Dragon Sake.'],0x218d58:['Cannot favorite this summon.'],
0x21918c:['Choose a unit to drain.','АSelect БExit ЕЁSwitch Unit'],0x219218:['No unit can be drained.','БExit ЕЁSwitch Unit'],0x219290:['Choose the target level.','АConfirm БCancel ДChange Lv'],0x2192d0:['Choose a puppet.','АSelect БExit ВStatus ЗMaterialize'],
0x219914:['Clear Favorite'],0x219930:[' '],0x219934:[' '],0x219938:[' pcs.'],0x21993c:[' servings'],
0x219944:[' obtained!'],0x219950:[' received!'],0x21995c:[' used!'],0x219968:[' made!'],
0x219a34:['"'],0x219a3c:['now available!'],0x219a54:['can now be learned!'],0x219a68:['"'],0x219a70:['changed to'],0x219a7c:['Skill Points'],0x219a90:['increased!'],0x219a9c:[' '],0x219aa0:[' '],0x219aa4:['OK?','Yes','No'],0x219ab8:['Give this?'],0x219ac8:['Yes'],0x219ad0:['No'],0x219ad8:['New menu'],0x219ae8:[' '],0x219aec:['recipe'],0x219af8:['Recipe Memo'],0x219b08:['Inspiration!'],
0x219b18:['obtained!'],0x219b28:['EXP'],0x219b34:['points'],0x219b40:['refunded!'],
0x219b50:['Party ability "'],0x219b60:['Pirate Lunch'],0x219b6c:['Stone Search'],0x219b78:['"'],0x219b84:['obtained!'],0x219b94:['found!'],0x219ba4:['confiscated!'],0x219bb8:['level'],0x219bc4:['Learn this?'],0x219bd4:['Raise its level?'],
0x219be8:['Choose an affinity to raise.'],0x219c00:['Please choose.'],0x219c10:['Machine Rank +1'],0x219c24:['Yokai Rank +1'],0x219c38:['Spirit Rank +1'],0x219c4c:['Beast Rank +1'],
0x219c60:['Magna / Toris'],0x219c70:['Rexx / Aty'],0x219c84:['Protagonist'],0x219c8c:['Rai / Fair'],0x219c9c:['Young Student'],0x219ca8:['Student'],0x219cb0:['Adult Student'],0x219cbc:['Dragon Child'],0x219cc4:['Guardian Beast'],0x219ccc:['Pomnit'],0x219cd8:['Subaru'],0x219ce0:['Required participants'],
0x219cf8:['Clear favorite?'],0x219d0c:[' '],0x219d18:['Choose the'],0x219d2c:['summon.'],0x219d34:['Choose the'],0x219d48:['color.'],
0x21a228:['Miss'],0x21a3d0:['Equip the crafted stone?','Yes','No'],0x21a404:['Stone equipped.'],0x21a41c:['Swap Weapons'],0x21a438:['Choose a Summonite Stone.'],0x21a45c:['Change equipment?','Yes','No'],
0x21b858:['Not deployed.'],0x21b9b0:['Anti-Magic Zone'],0x21bd04:['No ingredients remain here.'],0x21bd40:['Elixir'],0x21bd48:['sold for b.'],
0x21ddf0:['How many will you buy?'],0x21de04:['How many will you sell?'],0x21de18:[' pcs.'],0x21de1c:['Price'],0x21de24:['Is this OK?','Yes','No'],0x21de50:['Buy this?'],0x21de60:['Yes'],0x21de68:['No'],0x21de70:['Required class not unlocked.'],0x21de90:['Cannot learn this.'],0x21dea0:['Cannot raise this level.'],
0x21e4c0:['Finish shopping?','Yes','No'],0x21e510:['No puppets to materialize.'],0x21e7f0:['Level up?','Yes','No'],0x21e81c:['Is this OK?','Yes','No'],0x21e848:['Finish leveling up?','Yes','No'],0x21e878:['Finish draining levels?','Yes','No'],0x21e8ac:['Class Change!'],0x21e8dc:['" only can be equipped.'],0x21e8f0:['Cannot use Unit Summon.'],0x21e910:['" only can take unit form.'],0x21e92c:['Cannot control this unit.'],0x21e94c:['Cannot join this battle.'],
0x21e96c:['Affinity and battle type','have not been set.'],0x21e9a0:['Battle type not set.'],0x21e9c4:['Choose a summon affinity.','Machine','Yokai','Spirit','Beast'],0x21ea04:['Choose a battle type.','Warrior','Summoner'],0x21ea5c:['Summon affinity: Yokai'],0x21eab0:['Battle type: Warrior'],
0x21eb40:['Materialize this puppet?','Yes','No'],0x21eb6c:['Cancel materializing?','Yes','No'],0x21eb9c:['Not enough medals.'],0x21ebb4:['Unavailable on this route.','Proceed anyway?','Yes','No'],0x21ec08:['Finish summon training?','Yes','No'],0x21eec8:['Extra usable equipment'],0x21ef0c:['Unequip'],0x21ef1c:['Unset'],0x21ef24:['Sub Battle'],0x21ef30:['Floor '],0x21ef34:['Halls'],0x21ef3c:['Battle A'],0x21ef44:['Battle B'],0x21ef4c:['Battle C'],0x21ef54:['Battle D'],0x21ef5c:['Battle']}
TEXTS.update({
0x21c738:['Quit?','Yes','No'],
0x21f6b0:['Start?','Yes','No'],0x21f7f8:['Start?','Yes','No'],
0x21f858:['Jackpot'],0x21f860:['1st Prize'],0x21f868:['2nd Prize'],0x21f870:['3rd Prize'],
0x21f878:['Miss'],0x21f880:['Big Catch'],0x21f888:['Big Fish'],0x21f890:['Odd Catch'],
0x21f89c:['Normal'],0x21f8a4:['No Catch'],0x21f8ac:['Treasure'],0x21f8b4:['Rare'],
0x21f8bc:['Great Success'],0x21f8c4:['Success'],0x21f8cc:['Failure'],
0x21f8d4:['Good'],0x21f8d8:['Fair'],0x21f8dc:['Poor'],0x21f8e4:['Just in Time'],
0x21f8f0:['Time Up'],0x21f8fc:['None Selected'],
0x21fa60:['Quit?','Yes','No'],0x21fa84:['The bait was stolen...']})

def sha(b):return hashlib.sha256(b).hexdigest()
def ui_lines(data,pos,limit=3):
 result=[]
 for _ in range(limit):
  start=pos
  while data[pos:pos+2]!=b'\0\0':
   pos+=2;assert pos-start<1024
  if pos==start:break
  result.append(data[start:pos]);pos+=2
 return result
def main():
 old=(ROOT/'work/output/0.1.74/EBOOT.elf').read_bytes();refs,users,_=references(old);entries=[]
 for va,english in TEXTS.items():
  if va not in refs:continue
  raw=ui_lines(old,va+192,len(english))
  # Native pools may end before a following separately referenced choice block.
  english=english[:len(raw)]
  for s,source in zip(english,raw):encode_dialogue(s,source.decode('cp932'))
  entries.append(dict(source_address=va,source_lines=len(raw),source_sha256=sha(b'\0\0'.join(raw)),english=english,bindings=refs[va]))
 dest=ROOT/'work/translation/en/menus_0.1.75/native.json'
 dest.write_text(json.dumps(dict(version='0.1.75',entries=entries),indent=2)+'\n',encoding='utf8')
 print(len(entries))
if __name__=='__main__':main()
