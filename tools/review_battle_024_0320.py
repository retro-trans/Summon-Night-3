"""Independent root meaning review; preview source-bound fixes before writing."""
import argparse,json
from battle_source_024 import ROOT,sha,ordered
FIXES={
321:("I'm still alive...",'The supposedly defeated brother speaks about himself in reply.'),
432:('Sometimes, when I use that sword,','Preserve the explicit occasional frequency.'),
435:('Sometimes, when I use that sword,','Preserve the explicit occasional frequency.'),
469:('Now, make them regret','One continuous counterattack command across two fragments.'),
470:('coming after us!!','Continue rather than duplicate the command.'),
501:('Now, make them regret','Same counterattack command in alternate battle route.'),
502:('coming after us!!','Continue rather than duplicate the command.'),
478:('How dare you make my little pal','Younger close companion; avoid implying biological kinship.'),
510:('How dare you make my little pal','Same companion relationship in alternate battle route.'),
491:("why don't you say it?",'Correct English question word order.'),
523:("why don't you say it?",'Correct English question word order.'),
495:("You understand, don't you?",'Rhetorical expectation rather than genuinely asking for confirmation.'),
527:("You understand, don't you?",'Same rhetorical expectation in alternate battle route.'),
402:('The power of my kin in the Machine World...','Retain the world-of-origin distinction.'),
408:('no number of lives will save us.','Idiomatic impossibility rather than a finite stock of lives.'),
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();rows=ordered();bindings={}
 for n in (320,400,480):
  path=ROOT/f'work/translation/en/battle_0.1.24/slice_{n:04d}.targets.json';bindings[str(path.relative_to(ROOT)).replace('\\','/')]=sha(path.read_bytes())
 fixes=[dict(resource=rows[n]['resource'],resource_row=rows[n]['resource_row'],source_sha256=rows[n]['source_sha256'],text=t,reason=reason) for n,(t,reason) in FIXES.items()]
 doc=dict(review_type='independent_meaning_review',reviewer='root',rows_in_slice=list(range(320,528)),rows_examined=list(range(315,528)),draft_inputs_sha256=bindings,corrections=fixes,uncertainties=['Brother/self at321 inferred from comic exchange and speaker reply.','478/510 younger companion relationship translated little pal without biological claim.','Full battle route playthrough not performed by reviewer.'])
 print(json.dumps(doc,indent=2))
 if a.write:(ROOT/'work/translation/en/battle_0.1.24/review_0320_0528.json').write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':main()
