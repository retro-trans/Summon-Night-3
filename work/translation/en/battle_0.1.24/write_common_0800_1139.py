import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'tools'))
from battle_source_024 import load, source_text
from dialogue_encoding import encode_dialogue

BASE = Path(__file__).parent

A = '''Master, give it your all!
Tonight we're having my special chowder
soup!
Now that I know that, I have to work up
a proper appetite, right?
Let's gooooo!!
Come on, you're boys, aren't you?
Don't hold back - go all out
and show them what you've got!
D-Don't egg them on!?
You're a woman; try acting
a little more like one...
Guts matter for girls too.
Alize, follow right
behind me!
Yes, Lady Tris♪
You're a young woman too, so
you should behave a little more
appropriately. For example...
Ugh...
There's another Ness now...
What makes a good woman isn't her
looks or figure, but what's inside
that counts!
I agree completely! Size is
a trivial matter before greater things.
You lose if you worry about it!
My friend,
with your strength and mine, we shall
never be caught off guard.
Okay, Leold!
Let's make this flashy!!
The little fry are swarming...
I'll crush every last one of you!
You're getting way too carried away!
Big sis, be careful, okay?
Thanks, Hasaha.
I'll beat them in a flash, so
wait just a little while!
Be careful, Recie.
If you think it's dangerous, run back
to where everyone else is.
Y-Yes...
B-But I...
I'll do my best!!
Hey, can you fire beams?
What about a full missile barrage!?
Or a rocket punch!?
I'm sorry...
I'm an older model...
Boo!
How boring...
Ouch, ouch...
My chronic bald spots have gotten worse,
so I can't continue fighting...
...What a joke!!
If we combine the power of angels
and demons, I think we'll become
invincible!
Yeah, yeah, sure...
Death is written on you, old man.
You're headed for the most miserable
dog's death imaginable! Hee hee hee...!
Living on in that discarded world,
deceived all the while, is more miserable.
That is why I will continue to defy it!
I will destroy that paradise built on lies
and at last give form to the world
the founders dreamed of...
Hee hee, are you sure?
At this rate,
you won't die well.
Yes, perhaps so.
Even so, I...
Hasaha, hurry and grow up
so you can help Lady Meimei,
all right?
...(nod)
Dragon God, until then,
keep trying... okay?'''.splitlines()

B = '''...I'll give you some candy.
It means nothing to me now.
Thanks...
Big sis, you're kind.
......
Fox spirits can read people's hearts, right?
...What does mine look like?
The color of a winter sky...
Cold and sad...
But very beautiful...
......
Ododo, do your best!
Let's gooo!
M-Marurur!
It's dangerous!?
You can do it,
so have a little more
confidence in yourself!
Y-Yes...
I-I-I'm doing my best!
Oh, I found a cutie♪
A girl? Or maybe...
a b-o-y?
Eek...!?
D-Don't look!?
If possible...
I don't want you to fight
on the front lines too much...
Hee hee, sorry.
I've already graduated from being
a saint who only gets protected.
...Ness?
Where were you looking just now?
N-No!
I-I wasn't looking at anything...!
???
???
He seems reckless, but he's ready
to accept everything.
That's how he's different from you.
But he has you by his side.
That's why he can smile
so freely.
...I hope so.
???
He seems reckless, but he's ready
to accept everything.
That's how he's different from you.
But he has you by his side.
That's why he can smile
so freely.
...I hope so.
???
Sometimes... I worry
that having me at his side
might be a burden...
Having someone at your back
can make you strong, too. Just
support him from behind!
You're right...
Yes, I have to keep trying!
???
Hmm...
Could there be a secret
in this island's food?
Or maybe it's an Imperial
military secret?
Hmm...
...Um, you two?
Please don't stare
at my body so much...
Battle only leads to more battle.
It's the same thing over and over...
Is it still painful for you?
Even if it was a promise, to live
endless time as an Observer...
...No, I'm all right.
Because you and Ex are here
to support me now...
...Tell me!
Why could the king endure it!?
In days of lies and despair,
why carry everything alone,
without even relying on friends...?
That is why he could remain king.
I'm sorry... That's all
I can find as an answer...'''.splitlines()

C = '''Well then, after we finish this,
shall we see who can drink more?
Heh, then I should work up
a good sweat first!!
All right, Keina,
give us your usual support, okay?♪
Honestly...
You never know when to stop.
Really, you are a handful!
Hey, Minith,
don't get too cocky and
run too far ahead, all right?
So there!
I don't want to hear that
from you, Forte!
Ha ha ha ha...
So... when is the wedding?
If you like, I could arrange it
for you...
La la la la la!!
Seeing you makes me nostalgic.
You remind me of her in school.
Huh?
F-Focus on the battle,
idiot!!
It's fine to be stubborn, but never
forget how you truly feel.
That is my advice to you.
O-Okay...
I think I understand...
Keep your body straight and your mind calm.
That is an archer's discipline.
Yes, I understand, Lady Keina♪
I don't think you can force it
or just let it drift away.
That's what the heart is like.
Accept it as it is.
I think that is where
people's strength comes from.
It's difficult...
But I want to be that way too.
Strong like you...
Don't overdo it, Alize.
What matters is doing
all that you can.
Y-Yes!
(I wonder if big brothers...
are like this...)
You're so serious.
Doesn't it tire you out,
being like that all the time?
It's in my nature...
Sometimes I am amazed at myself too.
Hey, Rocka...
Do I really seem that reckless?
That's not it.
Maybe I worry about you too much.
I'm sorry if it bothered you.
I-It's fine...
I don't dislike that
you care about me...
Hey, Ryugu,
don't run ahead by yourself.
Stay with the group, okay?
How annoying...
It reminds me of
what she used to be like...
You really are a rude man.
You should watch your
language a little more, you know?
I wasn't raised well,
so give me a break.
M-i-s-s?
Grrr...!?
It hurts to watch you...
Sometimes, learn to hide behind
someone and let them protect you.
W-What!?
H-Hey, that is none of your business!
Hey, if you keep daydreaming,
I'll turn you all into a beehive
at once, okay?
Who gave her...
something that dangerous...?
Good chance to show me the results
of your training in the City of Games,
then, isn't it?
Hah! Fine...
Don't underestimate me like before
and wet yourself in fear, got it!?
How's that! How's that!!
How's thaaaat!!!
What a tough opponent...
I may have no choice but to use
my secret technique.
Come on, Amer!
Show them what our training has done!
Yes, Master!
I'll show them a girl's true strength
with everything I've got!!'''.splitlines()

D = '''You're awfully skinny.
Are you eating properly?
You need to drink milk too, okay?
Mind your own business...
And I hate milk.
Don't get too carried away, or don't
come crying to me when you get hurt.
You too!
Don't you dare do something silly like
getting caught in a summoning spell!?
I'll show you the Golden Faction's
real strength, Minith!
Yes, let's do it...
Give it all you've got, Kerma!
I know how hard it is
to become an heir, but...
Aren't you trying too hard?
I think it would be fine
to cut yourself some slack.
Thank you...
That almost made me cry.
No, no, no!
You have good material to work with;
it would be such a waste!
I'll teach you makeup and everything else
later... okay?
Y-Yes...
Please teach me...
The flames of a heart burning bright...
Clearly, you are in love, aren't you?
An impossible love...
Yet you cannot give it up.
That is lingering attachment...
No, that is true love!
May angels bless you...
Please do your best!!
Our positions may be different,
but I wish you would trust me
more!
Even if I fall short, I want to be
more help to Phaiz
and to all of you...
Kerma...
Thank you...
Hee hee, such a cute face,
and so brave.
Ghost lady?
W-What...!?
Heh heh heh.
Your face inside is bright red♪
The greatest tag team of sea men,
is complete!!!
If only it were
one plus one...
Comedy is battle!
Being tough is never a loss
for a comedian!!
All right, here we go!
If we win, I'll treat you to anything,
so give it your all!
Omurice...
Make it an extra mega-large serving!!
If we win, I'll treat you to anything,
so give it your all!
Everything is...
for shrimp♪
Let's go, sworn brother!
This is war!!!
Right, sir!
I'll follow you all the way!!'''.splitlines()

# The source has one separate acknowledgement before the Keina address.  Keep
# it as its own event row instead of merging the two lines in the English.
ALL = A + B + C + D
keina = len(A) + len(B) + 32
ALL[keina:keina + 1] = ['Yes, I understand.', 'Lady Keina♪']

# These short bridge rows preserve the three event slots that otherwise became
# folded into adjacent English fragments during the initial line-for-line pass.
ALL.insert(len(A) + len(B) + 79, '...')
ALL.insert(len(A) + len(B) + len(C) + 2, '...')


def build(start, text):
    resource, rows, data = load(175)
    translations = {}
    for number, target in enumerate(text, start):
        row = rows[number]
        encode_dialogue(target, source_text(row, data))
        translations[row['id']] = dict(
            row,
            resource=175,
            resource_row=number,
            ordered_index=10000 + number,
            text=target,
            status='draft',
            notes='No source control tokens.',
        )
    end = start + len(text) - 1
    return {
        'assigned_range': [start, end],
        'rows_examined': {'ranges_inclusive': [[max(0, start - 5), min(1139, end + 5)]], 'count': min(1139, end + 5) - max(0, start - 5) + 1},
        'rows_in_slice': list(range(start, end + 1)),
        'translations': translations,
        'uncertainties': ['Rows marked ??? are unidentified speakers in the source.', 'Fragments and ellipses preserve the original event boundaries.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    assert len(ALL) == 340, len(ALL)
    segments = tuple((start, ALL[start - 800:start - 800 + 80]) for start in range(800, 1120, 80))
    segments += ((1120, ALL[320:]),)
    for start, text in segments:
        document = build(start, text)
        output = BASE / f'common_{start:04d}.targets.json'
        print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'start': start, 'count': len(document['translations'])}))
        if args.write:
            output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
