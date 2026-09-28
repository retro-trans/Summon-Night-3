"""Write Chapter 2 rows 1120-1199 after a dry-run validation."""
import argparse, hashlib, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue

OUT = Path(__file__).with_name('slice_1120.targets.json')
TEXT = {
1120:"I'd never have",1121:"lost...",1122:"I mean it!",1123:"Uh... right.",
1124:"Hey, the way you fought...",1125:"You're no amateur,",1126:"are you?",
1127:"I used to be an Imperial soldier.",1128:"But now I've quit",1129:"and teach this child.",
1130:"I was an Imperial soldier.",1131:"But now I quit",1132:"and teach this child.",
1133:"...",1134:"...",1135:"...",1136:"...",1137:"Hmph!",
1138:"Sonolar, that's enough.",1139:"You're making",1140:"a spectacle of yourself.",1141:"Urgh...",
1142:"Well, whatever the case,",1143:"we lost.",1144:"Cook us or roast us--",1145:"do as you please.",
1146:"That's not why",1147:"we fought you.",1148:"Just promise",1149:"not to attack us again,",1150:"and that's enough.",
1151:"You say that, but",1152:"that puts us in a difficult spot.",1153:"Just promise never",1154:"to attack us again,",1155:"and that'll be enough... I think?",
1156:"What!?",1157:"That's so noble, but",1158:"do you really think",1159:"we'd keep our promise?",1160:"If it comes to that...",
1161:"　Then it comes to that.",1162:"　I just won't hold back.",1163:"　Then it comes to that.",1164:"　That would be a problem.",
1165:"Then it comes to that.",1166:"I'll just keep at it",1167:"until you understand.",1168:"I'd rather not fight,",1169:"though...",
1170:"Then it comes to that.",1171:"It can't be helped.",1172:"Honestly, I don't want",1173:"to keep doing this, though...",
1174:"If it comes to that...",1175:"I just won't hold back.",1176:"Ugh...",1177:"If it comes to that...",1178:"...",1179:"...",1180:"...",1181:"...",1182:"That would be a problem.",1183:"Yeah...",1184:"Huh?",1185:"What the hell is that!?",1186:"A problem...?",1187:"That's so irresponsible!",1188:"That's not",1189:"the issue here!",1190:"That's true, but",1191:"...",1192:"Oh, but don't worry.",1193:"If they were the kind of people",1194:"who'd do that...",1195:"In that fight,",1196:"they would have targeted ▲ first,",1197:"right?",1198:"In that fight,",1199:"they would have targeted ▲ first,",
}

def sha(data): return hashlib.sha256(data).hexdigest()
def build():
    resource, rows, data = chapter_source(88)
    assert set(TEXT) == set(range(1120,1200))
    translations = {}
    for n in range(1120,1200):
        row = rows[n]; text = TEXT[n]
        source = data[row['source_offset']:row['source_offset'] + row['source_byte_length']].decode('cp932')
        assert text, n
        encode_dialogue(text, source)
        translations[row['id']] = {
            'id': row['id'], 'source_sha256': row['source_sha256'], 'source_offset': row['source_offset'],
            'source_byte_length': row['source_byte_length'], 'reference_instructions': row['reference_instructions'],
            'resource_row': n, 'text': text, 'status': 'draft',
            'notes': 'Preserves runtime token ▲.' if '▲' in source else 'No source control tokens.'
        }
    return {'resource_id': resource['id'], 'assigned_range': [1120,1199], 'rows_examined': {'ranges_inclusive': [[1100,1219]], 'count':120}, 'translations': translations, 'uncertainties': [], 'new_glossary_requests': []}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();doc=build()
    print(json.dumps({'mode':'write' if args.write else 'dry-run','resource_id':doc['resource_id'],'translation_count':len(doc['translations']),'sample':[(n,doc['translations'][next(k for k,v in doc['translations'].items() if v['resource_row']==n)]['text']) for n in (1120,1144,1161,1196,1199)]},ensure_ascii=False,indent=2))
    if args.write: OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__': main()
