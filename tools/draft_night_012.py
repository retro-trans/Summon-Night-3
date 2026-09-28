"""English-only night-conversation drafts, preview source-bound metadata before writing."""
import argparse,json
from chapter_source import chapter_source
from chapter_patch import FOLDER
from dialogue_encoding import encode_dialogue

DRAFTS={89:{11:'''No use...
I just can't sleep.
After everything that's happened,
I'm probably too wound up
to sleep...
This is a problem...
I just can't sleep.
So much has
happened that I still
can't settle down, perhaps?
I'll go out for a little
night air.
Still,
what a beautiful moon.
Looking at it, I almost
feel as if I could
be drawn into it...
The moon is
truly beautiful tonight.
Looking at it, I almost
feel as if I could
be drawn into it...
......
!?
Was it my imagination?
For a moment, I felt
as though someone
was watching me...
Was it my imagination?
For a moment, I felt
as though someone
was watching me...
Beep!
Whoa!?
Oh,
it's you, R.
Don't scare me like that.
Could it be
that you were the one
watching me just now?
Eek!?
Oh, R!
Don't startle me like that.
Could it be
that you were the one
watching me just now?
Boop?
Just kidding...
There's no way
it could've been you, right?
Just kidding...
Of course it wasn't you, right?
Beep! ♪
Meowww!
Whoa!?
Oh,
it's you, Teco.
Don't scare me like that.
Could it be
that you were the one
watching me just now?
Eek!?
Oh, Teco!
Don't startle me like that.
Could it be
that you were the one
watching me just now?
Meow?
Just kidding...
There's no way
it could've been you, right?
Just kidding...
Of course it wasn't you, right?
Meowww! ♪
Bibi!
Whoa!?
Oh,
it's you, Onibi.
Don't scare me like that.
Could it be''',91:'''that you were the one
watching me just now?
Eek!?
Oh, Onibi!
Don't startle me like that.
Could it be
that you were the one
watching me just now?
Bibi?
Just kidding...
There's no way
it could've been you, right?
Just kidding...
Of course it wasn't you, right?
Bibibi! ♪
Kyupi!
Whoa!?
Oh,
it's you, Quiupy.
Don't scare me like that.
Could it be
that you were the one
watching me just now?
Eek!?
Oh, Quiupy!
Don't startle me like that.
Could it be
that you were the one
watching me just now?
Kyu?
Just kidding...
There's no way
it could've been you, right?
Just kidding...
Of course it wasn't you, right?
Kyupipi! ♪
Thank goodness...
That...
The voice I heard before!?
Though only a single thread,
hope still held on.
You surely can...
Stop him, and
overcome despair.
Surely...
Hope...?
Despair...?
What are you talking about!?
Ah, no...
I can't... any longer...
Please...
Stop...
me...!
...!?
What was that?
Just now...
What could
that have been?
Just now...'''},90:{11:'''Still, you know...
I never thought we'd actually
end up joining a pirate crew.
▲, you still
can't accept it?
You still can't accept it,
▲?
Of course not! If they hadn't
attacked our ship in the first place...
None of this
would have happened.
Yeah...
But, you know, if I
put all that aside,
I actually like
the people here pretty well.
Their captain Kyle, for instance,
is so manly and cool.
I see...
Yaaawn...
Come on, you should get some sleep.
It's been a while since you had a bed.
Come on, why don't you get some sleep?
It's been a while since you had a bed.
Yeah, you're right.
I think I will...
Sleep without worrying.
No matter what happens,
I'll keep my promise...
Don't worry...
No matter what happens,
I'll keep my promise...'''},91:{11:'''Sigh...
Huh? What's wrong?
Are you feeling ill?
Is something wrong?
Are you feeling ill, perhaps?
I'm simply appalled
at how brazen you are!
Honestly, volunteering to join pirates
is utterly outrageous!
▲, you still
can't accept it?
You still can't accept it,
▲?
Of course not! If those people hadn't
attacked the ship in the first place...
I would never have had to endure
all this inconvenience!
Yeah...
But, well...
Given the emergency,
I don't intend to
criticize your decision.
Scarrel, was it?
I did rather enjoy what he had to say.
I see...
Yaaawn...
Come on, you should get some sleep.
It's been a while since you had a bed.
Come on, why don't you get some sleep?
It's been a while since you had a bed.
But...
It's all right.
I'll handle it if anything happens.
Don't worry.
Your teacher is here if you need me.
Y-yes, of course...
That is your duty as my servant.
I'll put my trust in you, so do your utmost.
...Understood?
Yes, it would help
if you trusted me.
Yes, I'd be happy
if you trusted me.
Sleep without worrying.
No matter what happens,
I'll keep my promise...
Don't worry...
No matter what happens,
I'll keep my promise...'''} }

DRAFTS.update({92:{11:'''I still can't believe it.
To think we'd end up
joining pirates...
▲, you still
can't accept it?
You still can't accept it,
▲?
I'm sorry!?
That's not what I meant...!
It's just...
I'm worried...
Yeah...
When I was talking to Sonolar
earlier, I realized something.
Those people are
no different from us.
So I want to trust them, too.
I'm still worried... but that's how I feel.
I see...
Yaaawn...
Come on, you should get some sleep.
It's been a while since you had a bed.
Come on, why don't you get some sleep?
It's been a while since you had a bed.
Oh, yes...
Good night, Teacher.
Sleep without worrying.
No matter what happens,
I'll keep my promise...
Don't worry...
No matter what happens,
I'll keep my promise...'''},93:{11:'''I'm speechless.
To think you would really
rely on pirates.
▲, you still
can't accept it?
You still can't accept it,
▲?
Of course not! If those people hadn't
attacked the ship in the first place...
We would have reached the factory-ship city
long ago by now...
Yeah...
The leader's a brute, and his crew consists of
an impudent girl and a carefree queen.
The only one who shows any intelligence
is that summoner, Yard.
Whoa...
Isn't that going a bit far?
Ah, ha ha ha...
Mmm...
Come on, you should get some sleep.
It's been a while since you had a bed.
Come on, why don't you get some sleep?
It's been a while since you had a bed.
But...
It's all right.
I'll handle it if anything happens.
Don't worry.
Your teacher is here if you need me.
I don't like how
baseless that assurance is,
but for now, I'll take your word for it.
Reluctantly...
Yes, it would help
if you trusted me.
Yes, I'd be happy
if you trusted me.
Sleep without worrying.
No matter what happens,
I'll keep my promise...
Don't worry...
No matter what happens,
I'll keep my promise...'''},99:{11:'''Hey, Teacher.
Might be odd for me to say this, but...
I'm surprised you took us up on our offer.
Honestly, I really am.
Is it that strange?
Is it really that strange?
Strange, or rather... teaming up so easily
with people you were just fighting...
Most would figure you're either really crafty
or the exact opposite.
Ha ha...
Then why did you ask me
to join you, Kyle?
Then let me ask you the same thing, Kyle.
Why did you invite me?
Well...
How do I put it? Just a feeling, but...
I felt like I could trust you.
Something men understand
about each other, I guess...
It's the same for me.
Oh, then
we're alike.
!
It was just a feeling, but I thought
I could trust you all.
I see...
Ha ha! Wah ha ha ha!
I just can't believe
someone with such
a hearty laugh
could be truly evil.
I just can't believe
people who laugh
so heartily
could be truly evil.'''},100:{11:'''Heh heh, Teacher...
Here, take this.
Is this a good-luck charm?
A good-luck charm?
It's to thank you for today. If you hadn't been there,
we would've been in real trouble.
Thank you.
I'll treasure it.
Thank you very much.
I'll take good care of it.
Everyone but us managed to escape
that strange storm...
I'm glad they did, of course,
but it suddenly got so lonely.
So I'm happy
you and your pupil are guests on our ship.
You're the first woman aboard
besides me, too.
Yeah...
That's all I wanted to say...
Well then, good night!
So she can
smile like that,
too...
Good night, Sonolar.
Let's talk about all sorts of things
again tomorrow...'''}})

DRAFTS.update({101:{11:'''Hellooo, Teacher?
A present from me.
Is this a hand mirror?
Oh, a hand mirror?
You're so lovely, darling.
You really must take care of your appearance.
Th-thanks...
Thank you very much.
Whew...
Still, you know...
I'm grateful
that you trust us.
Huh?
If you'd really wanted to, you could have beaten us
and taken this ship... Am I wrong?
Well...
I know, darling.
The thought never even crossed your mind.
But... anyone can get the wrong idea.
Don't forget that.
Well then, good night! ♪
Perhaps
he sees things
from a broader perspective
than anyone else...
Scarrel might
actually see things
from a much broader perspective
than I thought...'''},102:{11:'''I'm sorry...
I'm sure you have so many questions.
It's all right. You'll explain everything properly
tomorrow, won't you?
Then I'll wait.
I can wait
that long.
Thank you...
I was surprised, though.
So you're a guest on this ship too, Yard.
I was surprised, though.
So you're a guest on this ship too, Yard.
Scarrel...
He and I go back a long way.
I turned to that connection
and ended up staying here.
Oh...
I see...
●,
there is one thing I should tell you now.
There is one thing
I should tell you now.
The reason Kyle and the others attacked that ship
was me.
What!?
They were only trying to help me
out of a difficult situation!
Please believe that, at least.
I'm begging you...
Y-yeah...
Oh, yes...
I thought there must
be something behind it,
but it really wasn't
a coincidence...
I thought there must
be something behind it,
but it really wasn't
a coincidence...'''}})

DRAFTS.update({122:{11:'''What is it?
What do you want to apologize for?
Well, I rushed ahead on my own
and caused trouble for you and the others...
Well, I ran out on my own
and caused trouble for you and the others, Kyle...
...
Ow!?
Ouch!?
Don't say
such stupid things.
You're one of us now.
It's fine to cause us a little trouble!
Kyle...
Kyle...
Besides, even if you hadn't been there,
I'd have picked a fight in that situation.
I can't stand
the way they do things.
I see...
...Wait, then you punched me
for nothing!?
Oh...! Then I got scolded
for nothing!?
Oh...
I guess so?
What do you mean,
"I guess so"!?
What do you mean,
"I guess so"!?
Ugh, that
really hurt...
Ugh, that
really hurt...'''},123:{11:'''I can't believe even the imperial army
has come to this island!
Well, you made
short work of them, Teacher.
Yeah...
Mixed feelings, huh?
About fighting the army
you used to belong to...
......
Don't be too
hard on yourself.
You were doing your very best.
I saw you.
Sonolar...
Heh heh... Look, things are only going
to get busier from here.
Let's keep our spirits up!
...Okay?
Thank you...
Sonolar...'''},124:{11:'''You certainly
keep surprising me.
I never knew you were the type
to rush so far ahead.
I'm sorry...
I'm sorry...
Oh, I'm not
blaming you.
We meant to fight the imperial army anyway,
and their methods infuriated me.
So watching you go wild
was quite a relief! ♪
Ha ha ha...
I-Is that so?
I envy you.
You're so straightforward.
Huh?
Oh, it's nothing.
Just thinking aloud.
Scarrel...
What was he trying
to say?
Scarrel...
What was he trying
to say?'''},125:{11:'''Honestly, that was hard to hear.
What the Guardians told us...
Yeah... As someone who uses summoning,
it was difficult to take.
Yes... As someone who uses summoning,
it gave me a great deal to think about.
When I was in the faction, I never even considered
the will of the beings we summoned.
I thought of them
as disposable tools.
But you were different.
You tried to see things from their perspective.
I think that's admirable.
Not at all! I just followed my own ideas
and rushed ahead, you know?
Not at all! I just got carried away
and rushed out there, you know?
Even so, that's
not something everyone can do.
...
W-well...
I won't forget the reality
I've witnessed on this island.
As someone who uses summoning,
I must never forget...
Yeah...
I won't forget, either...
You're right...
It's something we
must never forget...'''}})

def prepare(num,start):
    _,rows,data=chapter_source(num);texts=DRAFTS[num][start].splitlines()
    assert len(texts)==min(80,len(rows)-start),(num,start,len(texts))
    result={}
    for n,text in enumerate(texts,start):
        r=rows[n];source=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');encode_dialogue(text,source)
        result[r['id']]={**r,'resource_row':n,'text':text,'status':'draft'}
    lo=max(11,start-20);hi=min(len(rows)-1,start+len(texts)+19)
    return dict(resource_id=f'00:{num:05d}',assigned_range=[start,start+len(texts)-1],rows_examined=dict(ranges_inclusive=[[lo,hi]],count=hi-lo+1),translations=result)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('resource',type=int);p.add_argument('start',type=int);p.add_argument('--write',action='store_true');a=p.parse_args();d=prepare(a.resource,a.start)
    print(json.dumps(dict(mode='write' if a.write else 'dry run',resource=a.resource,assigned=d['assigned_range'],examined=d['rows_examined'],sample=[(r['resource_row'],r['text']) for r in list(d['translations'].values())[:5]]),indent=2))
    if a.write:
        folder=FOLDER/f'{a.resource:04d}';folder.mkdir(exist_ok=True)
        (folder/f'slice_{a.start:04d}.targets.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
