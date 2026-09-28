"""Root review of shared rows880-1139; preview before --write."""
import argparse,json
from battle_source_024 import ROOT,sha,load
FIX={
891:'Mr. Timid, do your best!',899:"I-I-I'll do my best!",904:"D-Don't lift it up!",
917:'Seems reckless, yet ready',918:'to accept everything.',919:"That's the difference between you two.",920:'But with you there,',921:"it's easy to see why",922:'that smile is so carefree.',
925:'Seems reckless, yet ready',926:'to accept everything.',927:"That's the difference between you two.",928:'But with you there,',929:"it's easy to see why",930:'that smile is so carefree.',934:'that my being there',938:'offer your support from behind!',
984:'If you like, I could serve',985:'as your matchmaker...',
1001:'Neither getting swept away nor suppressing it',1002:'is the answer, I think.',
1034:'a certain someone back in the day...',
1046:'Th-That is none of your business!',1047:'Hey, keep daydreaming',1048:"and I'll fill you all with holes",1049:'at once, okay?',1050:'Who was it...',1051:'who gave her',1052:'something that dangerous...?',
1054:'of your training in the arena city,',1058:'and have your knees give out, got it!?',
1069:"You're awfully skinny.",1070:'Are you eating properly?',1071:'You need to drink milk too, okay?',1072:'Mind your own business...',1073:'And I hate milk.',1074:"Don't get too carried away.",1075:"Don't come crying to me when you get hurt!",1076:'Same goes for you!',1077:"Don't be so careless",1078:'that you get caught in my summoning spells!',
1079:"Let's show them the true strength",1080:'of the Gold Faction, Minith!',1081:"Yes, you're right...",1082:"Let's give it our all, Kerma!",1083:'I know that the responsibility',1084:'of being an heir',1085:'is no small matter, but...',
1101:"Yet I still can't give it up.",1102:"I'm clinging to it, aren't I...",1110:'more help to Paffel',
1120:'The mightiest brotherhood of men of the sea',
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();_,rows,_=load(175);bindings={}
 for n in (880,960,1040,1120):
  f=ROOT/f'work/translation/en/battle_0.1.24/common_{n:04d}.targets.json';bindings[str(f.relative_to(ROOT)).replace('\\','/')]=sha(f.read_bytes())
 corrections=[dict(resource=175,resource_row=n,source_sha256=rows[n]['source_sha256'],text=t,reason='Repair shifted fragments1046-1052/1069-1085, idiom, implied gender, or speaker relationship against source and adjacent replies.') for n,t in FIX.items()]
 d=dict(review_kind='independent_meaning_review',reviewer='root',assigned_rows=list(range(880,1140)),examined_rows=list(range(880,1140)),draft_inputs_sha256=bindings,corrections=corrections,uncertainties=['917-930 and934/938 leave third-person gender unspecified because duplicated source exists in alternate branches.','891 descriptive nickname Mr. Timid rather than invented proper name Ododo.','Arena city1054 remains descriptive rather than asserting a researched place-name.'])
 print(json.dumps(dict(rows=260,corrections=corrections),indent=2))
 if a.write:(ROOT/'work/translation/en/battle_0.1.24/review_common_0880_1139.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
