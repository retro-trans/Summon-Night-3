import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).parent
INPUT = BASE / 'common_0560.targets.json'
OUT = BASE / 'review_common_0560.json'
CORRECTIONS = {
    568: ('All that I am,', 'Restores the source’s object; the dedication verb belongs to the final split line.'),
    569: ('for your great ambition,', 'Keeps the stated purpose on its own source line.'),
    570: ('I shall offer...', 'Restores the source’s dedication verb without duplicating the preceding English.'),
    593: ('Correcting a husband\'s faults', 'Corrects 良人 from the generic “good man” to “husband.”'),
    594: ('is also a wife\'s', 'Preserves the split possessive phrase.'),
    595: ('duty, is it not!?', 'Completes the source’s rhetorical question.'),
    604: ('...You thieving cat!', 'Restores the jealousy insult “thief cat”; “alley cat” changes its meaning.'),
    607: ('Do not be jealous.', 'Corrects 嫉妬しないで, which was mistranslated as “Don\'t pity me.”'),
    608: ('It is a sad way to live...', 'Restores the source’s characterization of that life.'),
}


def build():
    document = json.loads(INPUT.read_text(encoding='utf8'))
    rows = {item['resource_row']: item for item in document['translations'].values()}
    return {
        'build_version': '0.1.24',
        'review_kind': 'independent_meaning_review',
        'source': 'work/source/original.iso, 01.DAT V4 SCRIPT child 1, resource 175',
        'draft_inputs_sha256': {'work/translation/en/battle_0.1.24/common_0560.targets.json': hashlib.sha256(INPUT.read_bytes()).hexdigest()},
        'slice_ranges_inclusive': [[560, 639]],
        'examined_rows': {'ranges_inclusive': [[555, 644]], 'assigned_row_count': 80, 'context_rows_each_side': 5, 'total_row_count': 90},
        'review_policy': 'Compared every draft row to its CP932 source and five adjacent rows at both slice edges. Corrections are limited to meaning or source-line-boundary errors.',
        'corrections': [
            {'resource': 175, 'resource_row': row, 'source_sha256': rows[row]['source_sha256'], 'text': text, 'reason': reason}
            for row, (text, reason) in sorted(CORRECTIONS.items())
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    document = build()
    print(json.dumps({'mode': 'write' if args.write else 'dry-run', 'correction_count': len(document['corrections'])}))
    if args.write:
        OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
