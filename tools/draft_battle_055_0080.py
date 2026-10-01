"""Author preview for remaining battle-event rows 80-159."""
import argparse
from battle_pass_055 import save
TEXT='''I was just
being stubborn, that's all.
After we went to all that trouble to seal the sword...
Curse the Imperial Army!
Let's go, R!
We'll use our own strength
to drive them off!
After all that trouble
to seal the sword...
Let's go, Onibi!
We'll use our own strength
to teach them
a lesson!
After all that trouble
to seal the sword...
Lend me your strength, Quiupy!
Together, let's drive
the Imperial Army away!
After we went to all that trouble to seal the sword...
Curse the Imperial Army!
Let's go, Teco!
We'll use our own strength
to make them give up!
(The only way to make them give up on the sword
is to show them
how hopelessly outmatched they are...)
Please understand,
Azlier...
Please, Azlier...
Try to understand...
How's that!
We did it, R!
We did it!
Thank you, Onibi!
Thank you, Quiupy!
All right!
We did it, Teco!
There has to be a way besides killing each other.
I...
will bring this battle
to an end!
There has to be a way besides killing each other.
I...
will bring this battle
to an end!
Come at me, ●!
You and I are the ones
who should bring this to a close!
All right...
But I still
haven't given up!
Very well...
But I still
haven't given up.
Not so fast.
I'm not letting you
get to my sister!
Out of my way, Ishlar!
I don't have time
to deal with you!
You're in my way!
I don't have time
to deal with you!
Let's settle this,
●!
...Yeah.
Yes... And then
we can make a new beginning!
Ahahahaha!
Go on, try forcing
those pretty ideals of yours on us!
Can you still move, Galeor?
If you can, help me!
We'll strike them down!
...Orders received!
I won't forgive
a single one of them!
Listen, everyone!
You can't take those assassins
head-on!'''.splitlines()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
    save(80,TEXT,[[70,167]],uncertainties=[
        {'rows':[103,104,105],'note':'Implicit target of overwhelming force is the Imperial Army in adjacent pupil alternatives; restore subject without assigning a protagonist gender.'},
        {'rows':[117,118,119,120,121,122,123,124],'note':'The vow crosses two boxes. Retain the first-box trailing I, then complete the vow in the next box rather than shifting the whole sentence.'},
        {'rows':[146,147],'note':'A new beginning renders the implied fresh start after settling the confrontation, rather than adding a specific new relationship.'},
        {'rows':[155,156],'note':'The source omits the object; the attacking enemies are indicated by the immediately preceding order to strike them down.'}
    ],omissions=[],notes='Read global rows 70-167 with full groups. Preserve dynamic protagonist token in rows 125 and 144. Canonical R, Onibi, Quiupy, Teco, Azlier, Galeor, Ishlar names are locked.',write=a.write)
