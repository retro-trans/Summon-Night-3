import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / 'tools'))
from chapter_source import chapter_source
from dialogue_encoding import encode_dialogue

BASE = Path(__file__).parent
TARGET = BASE / 'slice_1200.targets.json'
COMPILED = BASE / 'compiled.targets.json'
OUT = BASE / 'review_1256_addendum.json'
ROWS = (1256, 1257, 1258)

def sha(value):
    return hashlib.sha256(value).hexdigest()

def build():
    resource, rows, data = chapter_source(111)
    draft = json.loads(TARGET.read_text(encoding='utf-8'))
    by_row = {item['resource_row']: item for item in draft['translations'].values()}
    relevant = []
    for number in ROWS:
        item = by_row[number]
        source = rows[number]
        original = data[source['source_offset']:source['source_offset'] + source['source_byte_length']].decode('cp932')
        assert item['id'] == source['id']
        assert item['source_sha256'] == source['source_sha256']
        encode_dialogue(item['text'], original)
        relevant.append(item)
    compiled = json.loads(COMPILED.read_text(encoding='utf-8'))
    group = next(group for group in compiled['layout_groups'] if group['id'] == 'chapter_111_1256_1257_1258')
    assert tuple(group['resource_rows']) == ROWS
    current_assembled = ' '.join(item['text'] for item in relevant)
    assert group['text'] == current_assembled
    corrections = [
        {
            'resource_row': 1256,
            'source_id': relevant[0]['id'],
            'replacement_text': 'My name is Phlaiz.',
            'reason': 'The source begins Phlaiz’s self-introduction; Phlaiz is not identified as a Guardian.'
        },
        {
            'resource_row': 1257,
            'source_id': relevant[1]['id'],
            'replacement_text': 'I serve as advisor to',
            'reason': 'Moves the advisor relationship into a grammatical English clause continued by the next fragment.'
        },
        {
            'resource_row': 1258,
            'source_id': relevant[2]['id'],
            'replacement_text': 'this Guardian, Lord Falzen.',
            'reason': '護人 modifies Lord Falzen in the source, preserving his Guardian role and the honorific.'
        }
    ]
    for correction in corrections:
        number = correction['resource_row']
        source = rows[number]
        original = data[source['source_offset']:source['source_offset'] + source['source_byte_length']].decode('cp932')
        encode_dialogue(correction['replacement_text'], original)
    snapshot = [
        {'resource_row': item['resource_row'], 'id': item['id'], 'source_sha256': item['source_sha256'], 'text': item['text']}
        for item in relevant
    ]
    return {
        'resource_id': resource['id'],
        'review_type': 'semantic_addendum',
        'assigned_range': [1254, 1260],
        'rows_examined': {'ranges_inclusive': [[1250, 1275]], 'count': 26},
        'prior_review': 'review_meaning_1200.json',
        'relevant_draft': {
            'target_file': TARGET.name,
            'target_file_sha256': sha(TARGET.read_bytes()),
            'resource_rows': list(ROWS),
            'rows_sha256': sha(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8'))
        },
        'compiled_layout_observed': {
            'file': COMPILED.name,
            'group_id': group['id'],
            'resource_rows': group['resource_rows'],
            'assembled_text': current_assembled,
            'display_helper_word': group['display_helper_word']
        },
        'meaning_corrections': corrections,
        'normalizer_note': 'The project normalizer owns the Freize-to-Phlaiz spelling correction elsewhere; this addendum records the independent role/grammar correction.',
        'uncertainties': []
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = build()
    print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'reviewed_rows': len(ROWS), 'corrections': len(report['meaning_corrections']), 'assembled_text': report['compiled_layout_observed']['assembled_text']}))
    if args.write:
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
