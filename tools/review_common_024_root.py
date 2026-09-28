"""Root independent shared-dialogue review; preview before --write."""
import argparse,json
from battle_source_024 import ROOT,sha,load
FIX={
0:'All right, wherever you are,',1:'come at me!',
35:"...You're always",36:'getting into trouble, you know.',
38:"You're one to talk,",39:'Sonolar...',
94:'Kill on sight...',102:"Don't you dare slack off,",
109:"I'll lead the charge!",133:"I'm counting on you to watch my back! ♪",
148:'P-PROTECT...',149:'IN...STRUC...TOR...',152:'P-PROTECT...',153:'IN...STRUC...TOR...',
157:"I'll be first into battle!",162:'W-w-wait!',169:"Wouldn't you agree, Oni Princess?",
212:'Wh-where are you looking',213:'when you say that, me?!',222:"You don't have to tell me!",
224:"From now on, I'll make things easy for you,",225:'Professor!',226:'Ha ha!',227:"That's reassuring.",
228:'Nup,',229:'stay behind me',230:'and keep close, okay?',231:'Honestly...',232:"I'm not a kid anymore!",
233:'I kept my promise',234:'just as I said I would! ♪',235:"Now it's your turn, Professor,",236:'to keep your promise...',237:"isn't it?",238:'Ah, ha ha ha...',239:'That was...',
295:'I already have',296:'a prince, you know?',
309:'Machine World duet!',372:'the miracles of Sapureth,',
378:'EVEN SEALED BENEATH',379:'THAT PROTECTION...',380:'YOUR WISHES...',381:'THIS UNIT WILL CARRY THEM ON!!',
}
REASONS={133:'Restore who entrusts the rear guard to whom.',149:'Dono is an honorific, not English do not.',153:'Dono is an honorific, not English do not.',162:'Stammer before matte (wait), not mother.',169:'Oni princess addresses Misumi, not the summon Onibi.',295:'Already has a prince, not timely arrival.',296:'Complete idiom already has a prince.',309:'Unison/music metaphor rather than political union.',378:'Protection is not established as an English proper name; preserve metaphor.',379:'Protection is not established as an English proper name; preserve metaphor.',380:'Wishes/intent carried on, rather than merely feelings.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();_,rows,_=load(175)
 bindings={}
 for n in range(0,400,80):
  f=ROOT/f'work/translation/en/battle_0.1.24/common_{n:04d}.targets.json';bindings[str(f.relative_to(ROOT)).replace('\\','/')]=sha(f.read_bytes())
 fixes=[dict(resource=175,resource_row=n,source_sha256=rows[n]['source_sha256'],text=t,reason=REASONS.get(n,'Repair alignment at224-239, English grammar, idiom, or fragment duplication while retaining context.')) for n,t in FIX.items()]
 doc=dict(review_kind='independent_meaning_review',reviewer='root',assigned_rows=list(range(400)),examined_rows=list(range(400)),draft_inputs_sha256=bindings,corrections=fixes,uncertainties=['Row212-213 addresses another version of the speaker; retain the self-address rather than inventing a third person.','Protection378-379 rendered descriptively, no established proper English term.','Adjacent context within full0-399 examined; row400 onward outside this review.'])
 print(json.dumps(dict(rows=400,corrections=fixes),indent=2))
 if a.write:(ROOT/'work/translation/en/battle_0.1.24/review_common_0000_0399.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
