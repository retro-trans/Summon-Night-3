"""Full-meaning battle translation draft; preview before --write."""
import argparse,json
from battle_source_024 import ordered,ROOT,load,source_text
from dialogue_encoding import encode_dialogue
TEXT='''Strike that red metal box
and break it!
If the enemies are caught in the explosion,
it should deal
quite a lot of damage!
I see...
Leave it to me!
Whew...
I hope that makes up for it a little.
Yes!
Rooooooaaaar...
RROOOAAARRR!!!
A yokai from Silturn!
Eeeek!?
Y-you idiot, Kyle!
Ha ha ha!
Just as I thought,
we hit the jackpot!
This is no laughing matter,
you idiot!
Ha ha, don't be like that.
I'll show you
you're safe with me in charge!
...Yard.
That one stone
with the strange color...
Yes, I can sense it.
It seems to hold some kind of
powerful curse or sorcery.
If that power is released,
anyone nearby
will be in serious trouble.
Ha ha! Sounds interesting!
All right, Sonolar! Go for it!
Leave it to me!
Hey, come on!
Isn't there anyone
with a little more fight in them!?
That's our captain...
Amazing...!
Yes!
Ooooooh...!!
Here they come!
Sorry, everyone!
Why do I have
such terrible luck...?
Hee hee.
Then perhaps you can make up for it
with a dazzling performance?
Ugh...
All right! Just you watch!
I'll show you!
...That stone with the different color...
I can sense some kind of
curse coming from it...
...That stone with the different color...
I can sense some kind of
curse coming from it...
Well, if you're curious,
why not
give it a try?
Then I'll take care of it
while I'm at it!
How's that!
Ooh!
Nicely done! ♪
Yes!
GRAAAARRR!!
A-anyway,
we have to fight!
Sorry, everyone.
Looks like I picked wrong.
Don't worry about it!
But I'm counting on you
to make up for it out there.
All right.
Perhaps it's time I got serious?
...Hmm!
That's the smell of gunpowder!
I mean, isn't it coming from'''.splitlines()

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 assert len(TEXT)==80,len(TEXT)
 rows=ordered()[160:240];out={}
 for r,t in zip(rows,TEXT):
  encode_dialogue(t,source_text(r,load(r['resource'])[2]));out[r['id']]=dict(r,text=t)
 doc=dict(translations=out,rows_examined=list(range(155,245)),rows_in_slice=list(range(160,240)),uncertainties=['Row174/179 aniki addresses Kyle; English uses his name/omits repeated kinship address.','Row177 jackpot conveys the dangerous big catch irony; review with surrounding scene.'],review_status='author_draft')
 print(json.dumps(dict(count=len(out),samples=list(out.values())[:2]+list(out.values())[-2:]),indent=2))
 if a.write:
  folder=ROOT/'work/translation/en/battle_0.1.24';folder.mkdir(parents=True,exist_ok=True)
  (folder/'slice_0160.targets.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
if __name__=='__main__':main()
