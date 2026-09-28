"""Write resource 134's translated opening dialogue slice."""
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools"))
from chapter_source import chapter_source
from dialogue_encoding import control_tokens, encode_dialogue

TEXT = {
0:"A little more to the right?", 1:"Yeah, that's it...", 2:"Heave... ho!", 3:"Heave... ho...",
4:"The lumber we cut down", 5:"I'll put it here, okay?", 6:"The lumber we cut down", 7:"Just as you said.",
8:"The branches have been cleared away.", 9:"Good work.", 10:"For now, this much", 11:"should be enough.",
12:"Then tell Kyle", 13:"to come back", 14:"for the time being, will you?", 15:"Yeah, got it.",
16:"Yes, understood.", 17:"Oh, I see.", 18:"Then let's call it", 19:"a day after this one.",
20:"Hold on a moment.", 21:"I'll be done soon.", 22:"Well then, I'll", 23:"take a little walk", 24:"around here.",
25:"Well then, I'll", 26:"take a little walk", 27:"around here.", 28:"All right, go on.",
29:"Taking a leisurely", 30:"look around like this, this island", 31:"really is rich in nature.",
32:"It kind of brings back memories", 33:"of the countryside...", 34:"Taking a leisurely", 35:"look around like this, this island",
36:"really is rich in nature, isn't it?", 37:"It somehow", 38:"brings back memories", 39:"of my village...",
40:"Auuugh...", 41:"...Huh?", 42:"...Yes?", 43:"Ah, auuugh???", 44:"What!?", 45:"Eek!?",
46:"Uuugh...", 47:"Whoa, hey!?", 48:"Hang in there!?", 49:"W-whoa!?", 50:"Please, hang",
51:"in there!?", 52:"This is dehydration, all right.", 53:"Huh?　Dehydration???", 54:"Auuugh???",
55:"Then, water...", 56:"Then, some water...", 57:"...!?", 58:"Mmph... gulp!", 59:"Gulp, gulp...!!",
60:"Hey!?", 61:"If you drink it", 62:"all at once, it could poison you...", 63:"Hey!?", 64:"If you drink it",
65:"all at once, it could poison you...", 66:"Still, that's some", 67:"serious drinking.",
68:"Pah... haaah!", 69:"I'm alive again!!", 70:"Though if it were alcohol,", 71:"it would have been", 72:"even better...",
73:"Huh?", 74:"So what, then?", 75:"You came all this way", 76:"just to drink good liquor...?",
77:"That's right.　I haven't had anything to drink", 78:"for quite a while now.", 79:"Nyahahaha!♪",
}

def payload():
    resource, rows, data = chapter_source(134)
    translations = {}
    for n in range(80):
        r = rows[n]
        source = data[r['source_offset']:r['source_offset']+r['source_byte_length']].decode('cp932')
        text = TEXT[n]
        assert control_tokens(text) == control_tokens(source), n
        assert text.count('\u3000') == source.count('\u3000'), n
        encode_dialogue(text, source)
        translations[r['id']] = {
            'id': r['id'], 'source_sha256': r['source_sha256'],
            'source_offset': r['source_offset'], 'source_byte_length': r['source_byte_length'],
            'reference_instructions': r['reference_instructions'], 'resource_row': n,
            'text': text, 'status': 'draft',
            'notes': 'Translated with rows 0-99 examined for scene and branch context.'
        }
    return {'resource_id': resource['id'], 'assigned_range': [0,79],
      'rows_examined': {'ranges_inclusive': [[0,99]], 'count': 100},
      'translations': translations,
      'uncertainties': [{'resource_rows':[60,65], 'note':'The warning literally invokes poison; rendered as a warning that drinking so quickly could poison the person, though the intended risk may be choking or illness.'}],
      'new_glossary_requests': []}

def main():
    a=argparse.ArgumentParser(); a.add_argument('--write',action='store_true'); args=a.parse_args()
    out=Path(__file__).with_name('slice_0000.targets.json'); doc=payload()
    print(json.dumps({'mode':'write' if args.write else 'dry-run','rows':len(doc['translations']),'sample':list(doc['translations'].values())[:2]+list(doc['translations'].values())[-2:]},ensure_ascii=False,indent=2))
    if args.write:
        if out.exists(): raise FileExistsError(out)
        out.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'wrote':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__=='__main__': main()
