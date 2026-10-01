"""Author preview for the first remaining battle-event slice."""
import argparse
from battle_pass_055 import save

TEXT = '''Come on, lads!
It's war!
Aye, Captain!
To think someone
stole the Summonite Stones...
This is what happens
when a man lives alone!
Grumble, grumble...
At your age,
you should have settled down!
Grumble, grumble...
Give me a break already...
Seriously...
All right, Mr. Whiskers!
It's time for your punishment!
Yikes! It's you!?
H-hmph!
What can you possibly do
when you're that tiny!?
Grrrr!
Marurur will show you
her secret weapon!
And I was having
such a lovely day off...
I was having
such a lovely day off...
Such a lovely day off...
Eeeeek!?
Am I
completely done for!?
Hiii! ♪
How've you been, meow?
Yeeeeeek!?
Why did such an all-star lineup
have to show up today of all days!?
I'll beat down
everyone who gets in our way!
Awoooooo!!
Ugh!
There are so many of them...
It's creepy!
If we each take down one,
we'll be done in no time!
Let's go!
Whaaat!?
Hold on, Big Bro!
All right!
We've all met our quota now!
This is a perfect opportunity...
I think I'll take that sword
off your hands right here!
Everyone, be careful.
That summoner...
is up to something!
Then we'll just have to strike
before we get hit!
You call yourselves friends,
but this is all it amounts to.
You turn on each other and cause pain so easily.
Ahahahaha! ♪
What a pathetic
bunch you are!
Ishlar...
You're going to take
those words back!
That's cruel...
Please take back
what you just said!
Ahahaha!
Try making me!
I've put you through a lot.
But now...
I won't waver anymore!
Yes, Sister!
Let's protect everything
that person loved, together!
Please forgive me.
All this time, I never understood
the pain you were carrying...
Don't worry about it.'''.splitlines()

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    save(0,TEXT,[[0,92]],
         uncertainties=[
             {'rows':[13,14],'note':'Descriptive Higehige-san rendered Mr. Whiskers; refers to the bearded pirate, not a new character name.'},
             {'rows':[19,20,21],'note':'Marurur retains third-person self-reference and the established fairy identity; secret weapon renders totteoki, not a named attack.'},
             {'rows':[73,74,75],'note':'Sister is the in-law form of address; that person preserves the source reference without asserting a gender.'},
             {'rows':[76,77,78],'note':'The apology and forgiving reply support restoring never understood; the Japanese trails off after the addressee\'s suffering.'}
         ],
         omissions=[{'rows':[3,4],'note':'Source is an unfinished complaint; English keeps the trailing thought after the theft.'}],
         notes='Read complete VM groups through global row 92, including the reply spanning rows 79-81. Gendered Marurur self-reference follows established character context; no character is inferred from raw speaker IDs.',
         write=a.write)
