"""English sprite targets for all seven minigames, including small variants."""
import json
from sn3_archive import ROOT
ENTRIES=[]
def add(root,ch,sprites,text,kind='mini_label'):
 for n in sprites:ENTRIES.append(dict(bank='00.DAT',path=[root,ch],sprite=n,text=text,kind=kind))
for n in [49,51,53,55,57,59,61]:add(n,0,[0],f'help_{n}','page')
for root,ch,n,key in [(50,0,0,'scratch_board'),(52,0,0,'darts_board'),(54,4,20,'fishing_reward'),(54,8,1,'bait_menu'),(54,10,0,'fishing_pull'),(56,20,1,'whack_results')]:add(root,ch,[n],key,'frame')
for n in [11,13,15]:add(52,6,[n],'Win!')
add(52,6,[19],'Miss')
for n,text in zip(range(4,10),['Worm','Dried Sardine','Dried Squid','Dough Bait','Shrimp','Golden Lure']):add(54,8,[n],text)
add(54,12,[1],'Mash!')
for ch,n,key in [(4,21,'fishing_ingredients'),(4,23,'fishing_money'),(9,1,'bait_status'),(9,3,'fishing_exit'),(9,6,'fishing_cast'),(9,9,'fishing_mash')]:add(54,ch,[n],key,'frame')
add(50,5,[13],'scratch_reward','frame')
for n,text in zip(range(12,17),['Rank: FAILED','Rank: NORMAL','Rank: GOOD!','Rank: EXCELLENT','Rank: PERFECT']):add(56,20,[n],text)
add(60,3,[0],'lotus_footing','frame');add(60,3,[1],'lotus_position','frame');add(60,3,[14],'lotus_result','frame')
for ch,nums,text in [(4,[16],'Not Enough Stones'),(4,[17],'Press'),(4,[18],'Confirm'),(4,[19],'Stop!'),(4,[20],'Sold Out'),(4,[23],'Switch'),(4,[24],'Exit'),(5,[0],'Press'),(5,[1],'Confirm'),(5,[2],'Stop!'),(5,[3],'Sold Out'),(5,[4,5],'Jackpot!!'),(5,[14],'Not Enough Stones'),(5,[15,16],'Win!'),(5,[17],'Switch'),(5,[18],'Exit'),(5,[19,20],'Too Bad...')]:add(62,ch,nums,text,'slot_label')
def main():
 for e in ENTRIES:
  if e['kind']=='slot_label':
   e['text']={'Press':'Circle','Switch':'D-pad: Switch','Exit':'Cross: Exit'}.get(e['text'],e['text'])
 ENTRIES.append(dict(bank='02.DAT',path=[89,1],sprite=0,text='night_prompt',kind='frame'))
 folder=ROOT/'work/translation/en/menus_0.1.75'
 (folder/'minigames.json').write_text(json.dumps(dict(version='0.1.75',entries=ENTRIES),indent=2)+'\n',encoding='utf8')
 print(len(ENTRIES))
if __name__=='__main__':main()
