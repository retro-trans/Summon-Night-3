"""Battle draft slice 240--319; preview before --write."""
import argparse,json
from battle_source_024 import ordered,ROOT,load,source_text
from dialogue_encoding import encode_dialogue
TEXT='''that very suspicious-looking
barrel?
Be careful!
If it explodes nearby,
you won't get away unscathed!
Be careful!
If it explodes nearby,
you won't get away unscathed.
Ha ha, now that's
an interesting find.
All right, Sonolar! Go for it!
Leave it to me!
Let's make a big bang!
How's that?
Amazing...
Seeing those movements again,
it's clear this is no ordinary fighter...!
Yes!
Even among humans...
you seem to be
an especially vile specimen.
Such harsh words from such a pretty face,
eh, monster girl!?
...I won't forgive you.
What disgraceful tactics.
Even as a warrior,
you are the lowest of the low.
Shut up!
All that matters is winning!
Winning, you hear!?
...I'll put you in your place!
......
What the hell are you?
You can pretend to be human,
but a monster is still a monster!
...UNFORGIVABLE!
You used your filthy tricks
and really did a number on us.
Shut up!
All that matters is winning!
Winning, you hear!?
...●.
Leave this prey to me.
That's a poisonous mushroom!
Everyone, be careful
not to get too close!
That's a poisonous mushroom!
Please be careful
not to get too close!
Then let's make them
take the poison instead!
Regret what you've done...
Next time, I'll take your life!
NEVER
SHOW YOUR FACE AGAIN...!
Count yourself lucky to be alive.
All right! A great success!
Raaah! This means war!
All right, boys!
Get 'em!
Aye, Captain!
I'm telling you
to hear me out!
Oh, come on!
I'm telling you
to hear me out!
Grrr...!
Looks like they've gotten
even stronger...!
Blast it! In that case,
you get out there
and show 'em how strong we are!
Whaaat!?
Me!?
You're askin' a lot, brother!
Broooother!?
How dare you do that to my brother!
Ohhh! This is all because
I told you to go!
What a terrible thing... *sob*'''.splitlines()
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();assert len(TEXT)==80,len(TEXT)
 out={}
 for r,t in zip(ordered()[240:320],TEXT):
  encode_dialogue(t,source_text(r,load(r['resource'])[2]));out[r['id']]=dict(r,text=t)
 doc=dict(translations=out,rows_examined=list(range(235,325)),rows_in_slice=list(range(240,320)),uncertainties=['Rows254–256 praise observed movements without naming fighter.','Row290 poison transfer describes the environmental trick, not a specific status mechanic.'],review_status='author_draft')
 print(json.dumps(dict(count=len(out),samples=list(out.values())[:2]+list(out.values())[-2:]),indent=2))
 if a.write:
  folder=ROOT/'work/translation/en/battle_0.1.24';folder.mkdir(parents=True,exist_ok=True);(folder/'slice_0240.targets.json').write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
if __name__=='__main__':main()
