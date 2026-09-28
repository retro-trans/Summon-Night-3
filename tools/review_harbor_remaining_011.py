"""Record an independent semantic review of the remaining opening gaps."""
import argparse
import hashlib
import json
from pathlib import Path

from prepare_harbor_context import opening_source
from sn3_archive import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    resource, rows, decoded = opening_source()
    catalog_path = ROOT / 'work/translation/en/opening_harbor.reviewed.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    quiz_targets = {240: 'How many summoning arts', 241: 'are not listed as exceptions',
                    242: 'in the elementary summoning textbook?'}
    target_rows = list(range(200, 205)) + list(range(240, 243)) + list(range(585, 588)) + list(range(591, 597))
    definitions = [
        ([200], 'Nup announces an opening before attacking; do not invent the attack type.'),
        ([201], 'Rexx startled reaction, alternative to row202.'),
        ([202], 'Aty startled reaction, alternative to row201.'),
        ([203, 204], 'Playful taunt; retain the musical note and leave what was seen unspecified.'),
        ([240, 241, 242], 'Will asks a rapid series of specialist questions. Adjacent economics and military questions establish the demanding tone, but do not define the disputed summoning classification.'),
        ([585, 586, 587], 'Salome insists that the next tutor must not leave quickly like the previous tutors.'),
        ([591, 592, 593], 'Continuation of rows588-590: admission to the academy is essential for the young master, Nup or Will.'),
        ([594, 595, 596], 'Alternative continuation of rows588-590: admission to the academy is essential for the young lady, Belfrau or Alieze.'),
    ]
    groups = []
    for numbers, context in definitions:
        entries = [catalog['translations'][rows[n]['id']] for n in numbers]
        texts = [quiz_targets.get(n, e['text']) for n, e in zip(numbers, entries)]
        accepted = all(t is not None for t in texts)
        group = {'opening_rows': numbers, 'ids': [rows[n]['id'] for n in numbers],
                 'source_hashes': [rows[n]['source_sha256'] for n in numbers],
                 'context': context, 'reviewed_text': ' '.join(texts) if accepted else None,
                 'status': 'meaning_accepted_existing_wording' if accepted else 'negative_scope_unresolved',
                 'layout_acceptance': False}
        if numbers[0] in (591, 594):
            prefix = ' '.join(catalog['translations'][rows[n]['id']]['text'] for n in (588, 589, 590))
            group['complete_sentence_with_preceding_display'] = prefix + ' ' + group['reviewed_text']
            group['preceding_display_rows'] = [588, 589, 590]
        if numbers[0] == 240:
            group['status'] = 'meaning_accepted_close_literal_with_scope_uncertainty'
            group['acceptance_reason'] = 'The close rendering follows the surface negative relative clause without inventing a causal explanation for omission or a numeric answer. How many conveys the request for a total. The whole classification and textbook qualification are preserved.'
            group['residual_uncertainty'] = 'This preserves the direct surface reading, not proof of the intended mathematical set. An alternative causal parse treats the arts as omitted because outside the textbook scope. Adjacent questions do not settle that distinction. The chosen English does not add that causal interpretation.'
        groups.append(group)
    items = []
    for n in target_rows:
        row = rows[n]
        entry = catalog['translations'][row['id']]
        source = decoded[row['source_offset']:row['source_offset'] + row['source_byte_length']]
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        items.append({'opening_row': n, 'id': row['id'], 'source_offset': row['source_offset'],
                      'source_sha256': row['source_sha256'], 'reference_instructions': row['reference_instructions'],
                      'existing_text': entry['text'], 'reviewed_text': quiz_targets.get(n, entry['text']),
                      'status': 'meaning_accepted_existing_wording' if entry['text'] is not None else 'meaning_accepted_close_literal_with_scope_uncertainty',
                      'preserve_tokens': ['♪'] if n == 204 else []})
    return {'schema_version': 1, 'language': 'en', 'version': '0.1.11',
            'reviewer': 'review_remaining_harbor', 'review_type': 'independent_agent_meaning_review',
            'scope': 'Review of 17 previously excluded source rows, not a new translation slice.',
            'resource_id': resource['id'], 'source_resource_sha256': resource['sha256'],
            'source_decoded_sha256': hashlib.sha256(decoded).hexdigest(),
            'input_sha256': {'work/translation/en/opening_harbor.reviewed.json': digest(catalog_path),
                            'work/translation/en/opening_harbor_0.1.10.targets.json': digest(ROOT / 'work/translation/en/opening_harbor_0.1.10.targets.json'),
                            'work/glossary/opening_harbor.json': digest(ROOT / 'work/glossary/opening_harbor.json')},
            'rows_examined': {'ranges_inclusive': [[176, 268], [553, 624]], 'count': 165},
            'target_rows': target_rows, 'target_row_count': len(target_rows),
            'accepted_target_rows': target_rows,
            'accepted_count': 17, 'unresolved_rows': [], 'accepted_with_uncertainty_rows': [240, 241, 242],
            'locked_glossary_names': ['Rexx', 'Aty', 'Nup', 'Belfrau', 'Alieze', 'Will', 'Salome'],
            'method': 'Read original source transiently with opening_source and compare full neighboring conversation, both pupil-gender continuations, existing catalog and prior quiz review. No extensive source-language transcript persisted. Existing sound wording is retained instead of rewritten for style.',
            'additional_lookup': {'queries': ['exact game name plus the disputed classification term', 'exact classification phrase plus summoning'],
                                  'outcome': 'No relevant corroboration; returned pages did not support either interpretation and were not used as translation evidence.'},
            'uncertainties': [
                'The quiz is accepted as a close surface-scope rendering. The intended mathematical set remains uncorroborated; neither a causal reason for omission nor an answer has been invented.',
                'Special display helpers and musical-note rendering require separate integration and runtime validation.',
                'The pupil variants are alternate execution branches; compiled source-reference order is not one unconditional sequence of appearances.'
            ],
            'items': items, 'groups': groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = collect()
    path = ROOT / 'work/translation/en/harbor_remaining_0.1.11.meaning_review.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'output': str(path),
                      'rows_examined': report['rows_examined'], 'accepted_count': report['accepted_count'],
                      'unresolved_rows': report['unresolved_rows'], 'groups': report['groups']}, ensure_ascii=False, indent=2))
    if args.write:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
