"""Write resource 134 dialogue rows 160-239."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];sys.path.insert(0,str(ROOT/'tools'))
from chapter_source import chapter_source
from dialogue_encoding import control_tokens,encode_dialogue
TEXT={
160:"Come to think of it, Sonolar",161:"is good with guns, right?",162:"Come to think of it, Sonolar",163:"said they were good",164:"with guns, didn't they?",
165:"She dropped it in the sea",166:"and that was that.",167:"What a fool.",168:"Oh, so now",169:"she uses a knife...",
170:"Aah, honestly!",171:"Hurry up and let me",172:"fire a gun already!",173:"Hahaha...",
174:"But it seems",175:"it isn't something",176:"that can be fixed so easily.",177:"But it seems",178:"it isn't something",179:"that can be fixed so easily.",
180:"Handling a ship is one thing,",181:"but repairs are outside",182:"our area of expertise too.",183:"Is that how it is?",184:"Is that how it is?",
185:"Pirates may look sloppy,",186:"but we're actually strict about",187:"dividing up our roles.",188:"Kyle is the captain",189:"and helmsman, and Sonolar",190:"is the gunner, right?",
191:"Kyle is the captain",192:"and helmsman, and Sonolar",193:"is the gunner, correct?",194:"And then",195:"I'm the navigator and",196:"the adviser.",
197:"We can make temporary repairs,",198:"but serious repairs",199:"are a different matter.",200:"Especially since",201:"we're starting by making the parts.",202:"True...",
203:"If we had replacement parts,",204:"it would be a little",205:"easier, though.",206:"The faction had also studied ways",207:"to use the power hidden in the sword,",208:"but...",
209:"Other than using it to strengthen",210:"summoning arts,",211:"no one could do anything with it.",212:"No one in the past",213:"has ever been able to use it",214:"the way you do.",
215:"Is it a special method",216:"unique to the Imperial Army?",217:"That's not it!",218:"I'm only doing what the voice",219:"I hear in my head tells me",220:"to do...",
221:"I'm not doing anything",222:"that special!",223:"I'm only doing what the voice",224:"I hear in my head tells me",225:"to do...",
226:"A voice!?",227:"Y-yeah.",228:"Yes, that's right.",229:"That's the first I've heard of it...",230:"There is no record",231:"of the sword ever reacting that way.",
232:"I see...",233:"Is that so?",234:"I'll continue",235:"looking into it in my own way,",236:"but there is no precedent.",
237:"If you notice anything unusual,",238:"please come to me",239:"without hesitation.",
}
def payload():
 rsrc,rows,data=chapter_source(134);d={}
 for n in range(160,240):
  r=rows[n];s=data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932');t=TEXT[n];assert control_tokens(t)==control_tokens(s),n;assert t.count('\u3000')==s.count('\u3000'),n;encode_dialogue(t,s)
  d[r['id']]={'id':r['id'],'source_sha256':r['source_sha256'],'source_offset':r['source_offset'],'source_byte_length':r['source_byte_length'],'reference_instructions':r['reference_instructions'],'resource_row':n,'text':t,'status':'draft','notes':'Translated with rows 140-259 examined for immediate scene and branch context.'}
 return {'resource_id':rsrc['id'],'assigned_range':[160,239],'rows_examined':{'ranges_inclusive':[[140,259]],'count':120},'translations':d,'uncertainties':[{'resource_rows':[206,211],'note':'The organization name is generic in this source; rendered as faction pending a scene-level terminology pass.'}],'new_glossary_requests':[]}
def main():
 a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');x=a.parse_args();o=Path(__file__).with_name('slice_0160.targets.json');doc=payload();print(json.dumps({'mode':'write' if x.write else 'dry-run','rows':len(doc['translations']),'sample':list(doc['translations'].values())[:2]+list(doc['translations'].values())[-2:]},ensure_ascii=False,indent=2))
 if x.write:
  if o.exists():raise FileExistsError(o)
  o.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'wrote':str(o),'sha256':hashlib.sha256(o.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
