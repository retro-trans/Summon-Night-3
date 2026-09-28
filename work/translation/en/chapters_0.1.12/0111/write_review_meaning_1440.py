import argparse, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue

BASE = Path(__file__).parent
TARGET = BASE / 'slice_1440.targets.json'
OUT = BASE / 'review_meaning_1440.json'

def sha(value):
    return hashlib.sha256(value).hexdigest()

def build():
    resource, rows, data = chapter_source(111)
    draft = json.loads(TARGET.read_text(encoding='utf-8'))
    seen = {}
    for source_id, item in draft['translations'].items():
        row = item['resource_row']
        if 1440 <= row <= 1519:
            original = rows[row]
            source = data[original['source_offset']:original['source_offset'] + original['source_byte_length']].decode('cp932')
            assert source_id == original['id'] and item['source_sha256'] == original['source_sha256']
            encode_dialogue(item['text'], source)
            seen[row] = source_id
    assert set(seen) == set(range(1440, 1520))
    return {
        'resource_id': resource['id'],
        'assigned_range': [1440, 1519],
        'semantic_complete': True,
        'rows_examined': {'ranges_inclusive': [[1420, 1539]], 'count': 120},
        'reviewed_slices': [{'path': TARGET.name, 'sha256': sha(TARGET.read_bytes()), 'assigned_range': [1440, 1519]}],
        'reviewed_source_ids': [seen[row] for row in range(1440, 1520)],
        'meaning_corrections': [],
        'uncertainties': [
            {'resource_row': 1478, 'detail': '先に帰って asks the party to return ahead; "go back ahead of us" retains the direction, though its destination is deliberately implicit.'},
            {'resource_row': 1504, 'detail': 'The source honorific さん is omitted in the existing English form; this is a localization-style choice, not a meaning loss.'}
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
