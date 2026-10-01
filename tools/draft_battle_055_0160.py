"""Author preview for remaining battle-event rows 160-239."""
import argparse
from battle_pass_055 import save
TEXT='''Yes!
Let's weaken them with summon magic,
then strike!
How's that!
Now you know the strength
of an Imperial soldier!
All right!
Hissssss!
I wanted to forget it forever...
But I suppose that's impossible.
Hissssss!
Can I never escape...
this nightmare...?
Right now, we have to
save Scarrel
and the others!
Hold on,
Scarrel!
Yard!
You lowly Strays!
Learn to fear
the Queen of the Dead!
Her summon magic is dangerous!
We have to defeat her
as quickly as possible...
Guh...
You...!
...
Ugh...
How could I possibly...?
Please fall back.
I'll take it from here...
I'm relieved to see you're well...
Though I didn't want our reunion
to happen like this.
Shut up!
Traitor!
You ungrateful wretch...
Atone with your death!
I simply opened my eyes...
to the truth!
It's not fair...
You were the only one who got to escape.
Don't resent me...
Stop hanging your head.
You can fly free of that place too.
This time, you'll face me!
Let me warn you...
As you are now,
you cannot defeat me.
What an overwhelming presence...
Such strength...!
What an overwhelming presence...
Such strength...!
Let's leave it at that.
It's been a long time
since I enjoyed myself like this.
All this time...
that wasn't even their full strength...?
I'll show you... This is
my "truth"!
To kill each other...
That is the fate
of the Qualified!
That...
I refuse to accept it!
That...
I refuse to accept it!
A fight to the death against myself...
That could be entertaining too.
Here I come...
ISHLAR!
Here I come...!
Prepare yourself!
Come on! Come at me!
With those eyes full of rage,
come and kill me!
These are all dangerous opponents.
We'll be in trouble if the battle drags on!
Then before that happens,'''.splitlines()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    save(160,TEXT,[[151,248]],uncertainties=[
        {'rows':[179,180,181],'note':'Strays is the setting term for hagure; Queen of the Dead follows chapter16 glossary.'},
        {'rows':[201,202,203,204,205],'note':'The two apparent interlocutors share a stored speaker operand, so roles were not inferred from it. Raku ni naru is escape from their oppressive situation, supported by the metaphor of taking flight.'},
        {'rows':[217,218],'note':'Use neutral singular their because the source gives only that person; no gender is inferred from the combatant slot.'},
        {'rows':[228,229],'note':'Preserve the explicit self-versus-self deathmatch wording; do not infer a clone mechanism from this line alone.'}
    ],omissions=[{'rows':[210,211,212,213],'note':'Exclamatory observations retain source non-sentence form; no gendered pronoun is inserted.'}],
    notes='Read full VM groups 151-248. Check resource143 mode2 speaker operand during compilation; it is a native speaker value, not dialogue text.',write=a.write)
