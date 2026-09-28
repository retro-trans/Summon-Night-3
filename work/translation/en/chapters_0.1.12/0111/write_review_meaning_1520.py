import argparse, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue

BASE = Path(__file__).parent
TARGET = BASE / 'slice_1520.targets.json'
OUT = BASE / 'review_meaning_1520.json'

def sha(value):
    return hashlib.sha256(value).hexdigest()

def build():
    resource, rows, data = chapter_source(111)
    draft = json.loads(TARGET.read_text(encoding='utf-8'))
    seen = {}
    for source_id, item in draft['translations'].items():
        row = item['resource_row']
        if 1520 <= row <= 1599:
            original = rows[row]
            source = data[original['source_offset']:original['source_offset'] + original['source_byte_length']].decode('cp932')
            assert source_id == original['id'] and item['source_sha256'] == original['source_sha256']
            encode_dialogue(item['text'], source)
            seen[row] = source_id
    assert set(seen) == set(range(1520, 1600))
    corrections = [
        {'resource_row': 1526, 'source_id': seen[1526], 'replacement_text': "Not just my name--the others'", 'reason': 'Restores the possessive construction begun by 俺だけじゃない and avoids the ungrammatical draft clause "what everyone else is named".'},
        {'resource_row': 1527, 'source_id': seen[1527], 'replacement_text': 'names, and what kind of people', 'reason': 'Continues the list of the others\' names and personalities.'},
        {'resource_row': 1528, 'source_id': seen[1528], 'replacement_text': 'they are...', 'reason': 'Completes the personality clause without changing its referent.'},
        {'resource_row': 1532, 'source_id': seen[1532], 'replacement_text': "Not just my name--the others'", 'reason': 'Parallel player-choice branch: restores the possessive construction begun by 私だけじゃありません.'},
        {'resource_row': 1533, 'source_id': seen[1533], 'replacement_text': 'names, and what kind of people', 'reason': 'Continues the list of the others\' names and personalities.'},
        {'resource_row': 1534, 'source_id': seen[1534], 'replacement_text': 'they are...', 'reason': 'Completes the personality clause without changing its referent.'}
    ]
    for correction in corrections:
        row = correction['resource_row']
        original = rows[row]
        source = data[original['source_offset']:original['source_offset'] + original['source_byte_length']].decode('cp932')
        encode_dialogue(correction['replacement_text'], source)
    return {
        'resource_id': resource['id'],
        'assigned_range': [1520, 1599],
        'semantic_complete': True,
        'rows_examined': {'ranges_inclusive': [[1500, 1619]], 'count': 120},
        'reviewed_slices': [{'path': TARGET.name, 'sha256': sha(TARGET.read_bytes()), 'assigned_range': [1520, 1599]}],
        'reviewed_source_ids': [seen[row] for row in range(1520, 1600)],
        'meaning_corrections': corrections,
        'uncertainties': [
            {'resource_row': 1576, 'detail': '仲良くなりたい literally expresses wanting to get along; "be friends" is a natural English rendering, but is slightly more categorical.'}
        ]
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build()
    print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'reviewed': len(report['reviewed_source_ids']), 'corrections': len(report['meaning_corrections'])}))
    if args.write:
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
