"""Consolidate immutable opening drafts and independent meaning reviews; preview first."""
import argparse
from copy import deepcopy
import hashlib
import json
import re
from PIL import Image

from prepare_harbor_context import opening_source
from sn3_archive import ROOT
from dialogue_encoding import encode_dialogue, control_tokens

BASE = ROOT / 'work/translation/en'
DEST = BASE / 'opening_harbor.reviewed.json'
REPORT = ROOT / 'docs/opening_harbor_validation.json'
DOCUMENT = ROOT / 'docs/OPENING_HARBOR_TRANSLATIONS.md'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def joined_text(parts):
    result = ''
    for part in parts:
        # A source row can hold only the punctuation after a runtime name.
        # This affects the readable group text only; source-row targets stay intact.
        separator = '' if not result or part in ('.', ',', '!', '?', ';', ':') else ' '
        result += separator + part
    return result


def prepare():
    resource, source, data = opening_source()
    original = {row['id']: row for row in source[:641]}
    positions = {row['id']: i for i, row in enumerate(source[:641])}
    inputs, targets, reviews, slices = {}, {}, [], []
    screenshot_path = ROOT / 'work/ui/harbor_dialogue/index.json'
    screenshots = read(screenshot_path)
    inputs[screenshot_path.relative_to(ROOT).as_posix()] = digest(screenshot_path)
    assert screenshots['source_resource_sha256'] == resource['sha256']
    assert len(screenshots['screenshots']) == 4
    for item in screenshots['screenshots']:
        path = screenshot_path.parent / item['image_file']
        assert digest(path) == item['sha256']
        with Image.open(path) as picture:
            assert picture.size == (item['width'], item['height'])
        assert item['source_ids'] == [source[i]['id'] for i in item['opening_rows']]
        assert item['source_hashes'] == [source[i]['source_sha256'] for i in item['opening_rows']]
        inputs[path.relative_to(ROOT).as_posix()] = digest(path)
    for n in range(8):
        draft_path = BASE / f'opening_{n:03d}.targets.json'
        review_path = BASE / f'opening_{n:03d}.meaning_review.json'
        draft, review = read(draft_path), read(review_path)
        for path in (draft_path, review_path):
            inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        assert review['independent_review'] is True
        assert review['reviewed_target_sha256'] == digest(draft_path)
        assert draft['source_resource_sha256'] == resource['sha256']
        assert draft['source_decoded_sha256'] == resource['compression']['decoded_sha256']
        expected = {r['id'] for r in source[n*80:(n+1)*80]}
        assert len(expected) == 80 and expected == set(draft['translations'])
        coverage = {r['id']: r for r in review['coverage']}
        assert set(coverage) == expected
        assert not set(targets).intersection(expected)
        for key, row in draft['translations'].items():
            for field in ('source_offset', 'source_sha256', 'reference_instructions'):
                assert row[field] == original[key][field], (key, field)
            assert coverage[key]['source_sha256'] == row['source_sha256']
            result = deepcopy(row)
            result.update(opening_row=positions[key], draft_file=draft_path.relative_to(ROOT).as_posix(),
                          meaning_review_file=review_path.relative_to(ROOT).as_posix(),
                          status='meaning_reviewed' if row.get('text') else 'unresolved')
            targets[key] = result
        count = sum(bool(r.get('text')) for r in draft['translations'].values())
        assert review['verdict']['existing_draft_rows_reviewed'] == count
        slices.append({'file': draft_path.relative_to(ROOT).as_posix(), 'assigned': 80,
                       'drafted': count, 'meaning_reviewed': count,
                       'rows_examined_by_translator': draft['rows_examined'],
                       'rows_examined_by_reviewer': review['rows_examined']})
        reviews.append((review_path, review))

    # Two boundaries were jointly drafted by their neighboring-slice reviewers.
    # Require a third author's source comparison before treating them as independent.
    for first in (398, 559):
        path = BASE / f'opening_boundary_{first}.meaning_review.json'
        review = read(path)
        assert review['independent_review'] is True
        inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        for relative, expected_hash in review['reviewed_inputs_sha256'].items():
            assert digest(ROOT / relative) == expected_hash
        coverage = {r['id']: r for r in review['coverage']}
        assert set(coverage) == {source[i]['id'] for i in range(first, first+3)}
        for key, row in coverage.items():
            assert row['source_sha256'] == original[key]['source_sha256']
            assert row['reference_instructions'] == original[key]['reference_instructions']
        reviews.append((path, review))

    edits, applied = [], {}

    def apply(row, review_path, reason, group_ids=None):
        key = row['id']
        assert key in original, key
        assert row['source_sha256'] == original[key]['source_sha256']
        text = row['proposed_text']
        assert isinstance(text, str) and text
        if key in applied:
            assert applied[key] == text, ('Conflicting reviewed proposals', key, applied[key], text)
        applied[key] = text
        if key not in targets:
            assert positions[key] == 640, 'Only final boundary completion may extend assignments'
            targets[key] = {**original[key], 'opening_row': 640, 'text': None,
                            'text_role': 'queued_dialogue_line', 'context': 'Final protagonist reflection before the cabin conversation.',
                            'meaning_review_file': review_path.relative_to(ROOT).as_posix()}
        target = targets[key]
        if target.get('text') != text:
            edits.append({'id': key, 'opening_row': positions[key], 'before': target.get('text'),
                          'after': text, 'review': review_path.relative_to(ROOT).as_posix(), 'reason': reason})
        target['text'] = text
        target['status'] = 'meaning_reviewed'
        target.setdefault('applied_review_proposals', []).append({'review': review_path.relative_to(ROOT).as_posix(), 'reason': reason})
        if group_ids:
            target['group_ids'] = group_ids

    for review_path, review in reviews:
        for correction in review['required_meaning_edits']:
            if 'rows' in correction:
                for row in correction['rows']:
                    apply(row, review_path, correction.get('reason', 'Required meaning correction'), correction.get('group_ids'))
            else:
                apply(correction, review_path, correction.get('reason', 'Required meaning correction'))
        for proposal in review.get('coordinated_completion_proposals', []):
            if not proposal.get('status', '').startswith('meaning_accepted'):
                continue
            assert proposal.get('apply_together') is True
            ids = proposal['group_ids']
            assert set(ids) == {r['id'] for r in proposal['rows']}
            for row in proposal['rows']:
                apply(row, review_path, proposal['proposal_id'], ids)

    glossary_paths = [ROOT / 'work/glossary/entities.json', ROOT / 'work/glossary/opening_harbor.json']
    entries = []
    for path in glossary_paths:
        inputs[path.relative_to(ROOT).as_posix()] = digest(path)
        entries.extend(read(path)['entries'])
    harbor = read(glossary_paths[1])['entries']
    normalizations, corpus_hits = [], []
    # Case-sensitive aliases only; source context must identify the entity.
    # In particular, ordinary "nap" and the verb "will" are never replaced.
    for path in BASE.glob('*.json'):
        doc = read(path)
        for key, row in doc.get('translations', {}).items():
            if not isinstance(row, dict) or not isinstance(row.get('text'), str):
                continue
            for entry in harbor:
                for alias in entry.get('aliases', []):
                    if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', row['text']):
                        corpus_hits.append({'file': path.relative_to(ROOT).as_posix(), 'id': key,
                                            'alias': alias, 'canonical': entry['target_name'],
                                            'action': 'Preserved immutable input; normalize only reviewed successor with source context.'})
    for key, target in targets.items():
        sr = original[key]
        jp = data[sr['source_offset']:sr['source_offset'] + sr['source_byte_length']].decode('cp932')
        if not target.get('text'):
            continue
        target.setdefault('glossary_ids', [])
        for entry in harbor:
            if entry['source_name'] not in jp:
                continue
            if entry['id'] not in target['glossary_ids']:
                target['glossary_ids'].append(entry['id'])
            for alias in entry.get('aliases', []):
                before = target['text']
                after = re.sub(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', entry['target_name'], before)
                if before != after:
                    normalizations.append({'id': key, 'opening_row': positions[key], 'before': before, 'after': after, 'glossary_id': entry['id']})
                    target['text'] = after
        encode_dialogue(target['text'], jp)
        assert control_tokens(target['text']) == control_tokens(jp)
        assert target['text'].count('\u266a') == jp.count('\u266a'), key
        if target['text_role'] == 'choice_label' and jp.startswith('\u3000'):
            assert target['text'].startswith('\u3000'), key

    assert set(targets) == set(original), 'Final boundary completion missing'
    groups = {}
    for key, row in targets.items():
        ids = tuple(row['group_ids'])
        assert key in ids and set(ids).issubset(targets), ('Incomplete group', key, ids)
        for other in ids:
            assert tuple(targets[other]['group_ids']) == ids, ('Inconsistent group', key, other)
        groups[ids] = {'ids': list(ids), 'opening_rows': [positions[i] for i in ids],
                       'context': row['context'], 'text_role': row['text_role'],
                       'text': joined_text([targets[i]['text'] for i in ids]) if all(targets[i].get('text') for i in ids) else None}
        choices = [{'id': targets[i]['choice_id'], 'text': targets[i]['text']}
                   for i in ids if targets[i]['text_role'] == 'choice_label']
        if choices:
            groups[ids].update(kind='choices', choices=choices,
                               prompt=' '.join(targets[i]['text'] for i in ids if targets[i]['text_role'] != 'choice_label'))
    ordered_groups = sorted(groups.values(), key=lambda g: min(g['opening_rows']))
    unresolved = [r['opening_row'] for r in targets.values() if not r.get('text')]
    stats = {'assigned_source_rows': 640, 'additional_reviewed_boundary_rows': 1,
             'preserved_draft_nonempty_rows': sum(s['drafted'] for s in slices),
             'integrated_source_rows': len(targets), 'reviewed_target_rows': len(targets)-len(unresolved),
             'unresolved_rows': unresolved, 'display_or_choice_groups': len(groups),
             'complete_translated_groups': sum(g['text'] is not None for g in ordered_groups),
             'meaning_or_boundary_text_changes': len(edits), 'name_normalizations': len(normalizations)}
    catalog = {'schema_version': 1, 'language': 'en', 'resource_id': resource['id'],
               'source_resource_sha256': resource['sha256'], 'source_decoded_sha256': resource['compression']['decoded_sha256'],
               'scope': 'Opening source rows0–640: recollection, harbor/student branches and departure reflection. Row641 starts the cabin conversation. Compiled order is not an unconditional playthrough.',
               'status': 'independently_meaning_reviewed_not_built', 'statistics': stats, 'inputs_sha256': inputs,
               'meaning_and_boundary_edits': edits, 'glossary_normalizations': normalizations,
               'name_alias_corpus_scan': corpus_hits,
               'do_not_touch_glossary_terms': [e['target_name'] for e in harbor],
               'translation_process_order': ['Independent meaning review', 'Atomic boundary/meaning edits', 'Scripted glossary normalization'],
               'layout_and_runtime_accepted': False,
               'layout_followups': ['Measure/reflow all groups and choices; source row divisions are not English line breaks.',
                                    'Validate helper2058, musical note, punctuation-only row332 and runtime player-name expansion.',
                                    'Relocate complete groups without an original-byte budget; validate allocation, branch and save/load behavior.',
                                    'Identify and repack the native Adnias Harbor location-banner asset.'],
               'groups': ordered_groups, 'translations': dict(sorted(targets.items(), key=lambda item: item[1]['opening_row']))}
    report = {'schema_version': 1, 'scope': 'Static source, independent-review provenance, boundary, control-token and encoding checks; no runtime acceptance.',
              'checks': {'all_8_disjoint_80_row_assignments': True, 'all_source_hashes_and_references': True,
                         'all_four_screenshot_hashes_dimensions_and_anchors': True,
                         'all_independent_review_input_hashes': True, 'all_review_coverage_hashes': True,
                         'jointly_authored_boundaries_have_third_author_review': True,
                         'all_integrated_groups_complete': True, 'all_nonempty_targets_encode_and_preserve_tokens': True,
                         'meaning_edits_before_glossary_normalization': True},
              'statistics': stats, 'opening_slices': slices, 'inputs_sha256': inputs,
              'meaning_and_boundary_edits': edits, 'name_normalizations': normalizations,
              'whole_target_corpus_alias_hits': corpus_hits, 'unresolved_rows': unresolved}
    lines = ['# Opening and Adnias Harbor dialogue', '',
             f"{stats['reviewed_target_rows']} independently reviewed English target rows across {len(groups)} display/choice groups; {len(unresolved)} unresolved rows. These are source fragments and alternate branches, not that many complete sentences.", '',
             'This pass covers opening source rows 0–640, through the departure reflection. The next cabin conversation starts at row641. Original drafts and reviews are preserved; this document uses the reviewed successor catalog after complete-group fixes and glossary normalization.', '',
             '**Not yet inserted into the game.** The playable image remains 0.1.4. English below is full-meaning text, not final measured line breaks.', '',
             '## Your screenshots', '']
    for title, wanted in [('Cold and hunger', [121,122,123]), ('Remembering the ship', [109,110]), ('Surprise at the new job', [158,159,160])]:
        lines += [f"- **{title}:** " + ' '.join(targets[source[i]['id']]['text'] for i in wanted)]
    lines += ['- **Location banner:** Imperial Territory: Adnias Harbor', '',
              'Adnias Harbor and Pastis are project romanizations; no attested English location spelling was found. Character spellings follow the [current series wiki](https://summonnight.wiki.gg/wiki/Summon_Night_3); research and exceptions are recorded in [the harbor glossary](../work/glossary/opening_harbor.json).', '',
              '## Complete reviewed sequence', '',
              'Branches are shown in compiled source order. Each group retains its original branch/context metadata in the [catalog](../work/translation/en/opening_harbor.reviewed.json). The ● symbol is the player name supplied at runtime.', '']
    for group in ordered_groups:
        row_label = ', '.join(map(str, group['opening_rows']))
        lines += [f"### Rows {row_label}", '']
        if group.get('kind') == 'choices':
            if group['prompt']:
                lines += [group['prompt'], '']
            lines += [f"- Choice {choice['id']}: {choice['text'].strip()}" for choice in group['choices']]
            lines += ['']
        else:
            lines += [group['text'] or '*Unresolved: excluded from any translated insertion until meaning is settled.*', '']
        lines += ['<details>', '<summary>Branch and source context</summary>', '', group['context'], '', '</details>', '']
    lines += ['## Remaining implementation work', '', *['- '+s for s in catalog['layout_followups']], '',
              'See [static validation](opening_harbor_validation.json) for hashes, exact counts and applied review changes. Retained uncertainty notes remain in each independent review; meaning acceptance does not establish measured fit or runtime behavior.', '']
    return catalog, report, '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    catalog, report, document = prepare()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destinations': [str(p) for p in (DEST, REPORT, DOCUMENT)],
                      'statistics': catalog['statistics'], 'checks': report['checks'],
                      'meaning_edits': catalog['meaning_and_boundary_edits'],
                      'normalizations': catalog['glossary_normalizations'],
                      'samples': [g for g in catalog['groups'] if any(r in (109,121,158,240,331,398,479,559,639) for r in g['opening_rows'])]}, ensure_ascii=False, indent=2))
    if args.write:
        assert not any(p.exists() for p in (DEST, REPORT, DOCUMENT)), 'Refusing to overwrite preserved artifacts'
        for path, value in ((DEST, catalog), (REPORT, report)):
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        DOCUMENT.write_text(document, encoding='utf-8')


if __name__ == '__main__':
    main()
