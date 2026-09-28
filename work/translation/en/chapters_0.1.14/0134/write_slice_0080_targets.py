"""Write resource 134 dialogue rows 80-159."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]; sys.path.insert(0,str(ROOT/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import control_tokens,encode_dialogue
TEXT={
80:"This person's a total",81:"mess...",82:"Oh, I see!",83:"So that's why it was dehydration.",84:"Don't accept that so easily!?",85:"Honestly...",
86:"Well, still,",87:"collapsing like that",88:"was completely outside my calculations.",89:"I only avoided becoming jerky",90:"thanks to",91:"you all...",
92:"Yes, I really should",93:"thank you for this.",94:"Come along with me.",95:"Okaaay!",96:"Welcome to",97:"Meimei's shop!♪",
98:"A shop...?",99:"Whaaat!?",100:"Why is something like this",101:"in a place like this???",
102:"Meimei's shop's specialty is that",103:"you can use it easily",104:"anywhere, anytime.",105:"That doesn't",106:"answer the question...",
107:"Ah, is that",108:"how it works?",109:"Hmm, hmm...",110:"Would these be the goods",111:"that suit you two?",
112:"Hey, hey!?",113:"Isn't this a new",114:"pirate flag!?",115:"And this is a textbook?",116:"This one's a textbook.",
117:"They're indispensable for",118:"teachers and pirates, aren't they?",119:"Nyaha, nyahahaha!",120:"Y-yeah...",121:"Thank you.",122:"This helps a lot.",123:"...",
124:"I'll sell you other goods too,",125:"as long as",126:"you pay for them.",127:"Take your time",128:"looking around.",129:"Nyahahahaha!♪",
130:"Hmm...",131:"This island really does have",132:"a lot of odd people.",133:"No, that person",134:"felt especially odd",135:"even among them, though???",
136:"But they were a nice person.",137:"No, that's not",138:"the point...",139:"You're hardly",140:"in a position",141:"to say that...",
142:"Good grief...",143:"You two are plenty",144:"odd yourselves.",145:"Still, it's surprising",146:"they guessed both your occupations",147:"just by looking at you.",
148:"Perhaps that person",149:"has some kind of",150:"special power.",151:"Well, who cares?",152:"That shop definitely",153:"is convenient.",
154:"They even had a pretty",155:"good selection of weapons.",156:"Hey, did they have guns!?",157:"No, not",158:"that far...",159:"What!?"
}
def payload():
 rsrc,rows,data=chapter_source(134);d={}
 for n in range(80,160):
  r=rows[n];source=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');text=TEXT[n]
  assert control_tokens(text)==control_tokens(source),n;assert text.count('\u3000')==source.count('\u3000'),n;encode_dialogue(text,source)
  d[r['id']]={'id':r['id'],'source_sha256':r['source_sha256'],'source_offset':r['source_offset'],'source_byte_length':r['source_byte_length'],'reference_instructions':r['reference_instructions'],'resource_row':n,'text':text,'status':'draft','notes':'Translated with rows 60-179 examined for immediate scene context.'}
 return {'resource_id':rsrc['id'],'assigned_range':[80,159],'rows_examined':{'ranges_inclusive':[[60,179]],'count':120},'translations':d,'uncertainties':[{'resource_rows':[89,91],'note':'The speaker calls themself dried fish/jerky figuratively; rendered as jerky to retain the joke.'}],'new_glossary_requests':[]}
def main():
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');x=a.parse_args();o=Path(__file__).with_name('slice_0080.targets.json');doc=payload();print(json.dumps({'mode':'write' if x.write else 'dry-run','rows':len(doc['translations']),'sample':list(doc['translations'].values())[:2]+list(doc['translations'].values())[-2:]},ensure_ascii=False,indent=2))
 if x.write:
  if o.exists():raise FileExistsError(o)
  o.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'wrote':str(o),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
