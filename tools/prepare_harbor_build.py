"""Select reviewed harbor text supported by the existing renderer; preview first."""
import argparse
import hashlib
import json
from pathlib import Path

from sn3_archive import ROOT
from prepare_harbor_context import opening_source
from dialogue_layout import PIXEL_PROFILE, DISPLAY_PROFILES, layout_dialogue, latin_width
from dialogue_encoding import control_tokens
from font_metrics import collect
from font_patch import PROFILE as FONT_PROFILE, FONT_POOL_CAPACITY
from sn3_vm import instructions
from verify_dialogue_layout import simulate_group

CATALOG = ROOT / 'work/translation/en/opening_harbor.reviewed.json'
DEST = ROOT / 'work/translation/en/opening_harbor_0.1.5.targets.json'
REPORT = ROOT / 'docs/harbor_build_layout_0.1.5.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    catalog = json.loads(CATALOG.read_text(encoding='utf-8'))
    for relative, expected in catalog['inputs_sha256'].items():
        if sha(ROOT / relative) != expected:
            raise ValueError('Reviewed input changed: ' + relative)
    resource, source, data = opening_source()
    if resource['sha256'] != catalog['source_resource_sha256']:
        raise ValueError('Source identity changed')
    original = {r['id']: r for r in source}
    targets = catalog['translations']
    by_row = {r['opening_row']: r for r in targets.values()}
    metrics = collect()[0]['characters']
    code = instructions(data)
    at = {i['offset']: i for i in code}
    menus = [[65,66,67,68], [176,177,178], [179,180,181], [394,395,396],
             [456,457,458], [459,460,461], [487,488,489], [490,491,492]]
    menu_rows = {n for menu in menus for n in menu}
    excluded, selections, groups, menu_evidence = [], {}, [], []

    def add(row):
        selections[row['id']] = {k: row[k] for k in ('source_offset', 'source_sha256', 'text')}
        selections[row['id']].update(status='meaning_reviewed', encoding_profile='dialogue_fullwidth_cp932')

    for menu in menus:
        rows = [by_row[n] for n in menu]
        measured = [{'opening_row': r['opening_row'], 'text': r['text'], 'cells': len(r['text']),
                     'pixels': latin_width(r['text'].replace('\u3000', ' '), metrics)} for r in rows]
        supported = all(r['cells'] <= 31 and r['pixels'] <= 208 for r in measured)
        menu_evidence.append({'rows': menu, 'measured': measured, 'included': supported,
                              'policy': 'Keep original menu code, option IDs and spacing; conservative 208px/31-cell single-line limit.'})
        if supported:
            for row in rows:
                add(row)
        else:
            excluded.append({'opening_rows': menu, 'reason': 'Complete menu retained in Japanese: long choice exceeds the current single-line layout limit.'})

    for group in catalog['groups']:
        numbers = group['opening_rows']
        if set(numbers).intersection(menu_rows):
            if not set(numbers).issubset(menu_rows):
                raise ValueError('Mixed menu/dialogue group')
            continue
        rows = [targets[k] for k in group['ids']]
        reason = None
        if not group['text']:
            reason = 'Meaning unresolved; original Japanese preserved.'
        elif any(control_tokens(r['text']) for r in rows):
            reason = 'Runtime player-name expansion needs a measured layout profile.'
        elif set(group['text']) - set(metrics):
            reason = 'Musical-note glyph has no validated metric in the existing layout profile.'
        else:
            cursor = rows[-1]['reference_instructions'][0] + 8
            while at[cursor]['opcode'] == 5:
                cursor += at[cursor]['size']
            if at[cursor].get('target_word') not in DISPLAY_PROFILES:
                reason = 'Special display helper has no accepted layout profile.'
        if reason:
            excluded.append({'opening_rows': numbers, 'reason': reason})
            continue
        for row in rows:
            add(row)
        groups.append({'id': 'harbor_rows_' + '_'.join(map(str,numbers)),
                       'source_offsets': [r['source_offset'] for r in rows]})

    selection = {'schema_version': 1, 'language': 'en', 'resource_id': resource['id'],
                 'source_iso_sha256': '00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda',
                 'scope': 'Reviewed opening/harbor test selection; unsupported complete groups/menus remain original Japanese.',
                 'layout_profile': PIXEL_PROFILE, 'required_font_profile': FONT_PROFILE,
                 'required_font_pool_capacity': FONT_POOL_CAPACITY,
                 'review_inputs_sha256': {**catalog['inputs_sha256'], CATALOG.relative_to(ROOT).as_posix(): sha(CATALOG),
                                         'tools/prepare_harbor_build.py': sha(Path(__file__))},
                 'layout_groups': groups, 'translations': selections,
                 'excluded_groups': excluded, 'menu_layout_evidence': menu_evidence}
    updated, changes, layouts = layout_dialogue(data, {r['source_offset']: r for r in selections.values()}, groups, PIXEL_PROFILE)
    # Every generated page must retain the same display call, arguments and continuation.
    for group in layouts:
        before = simulate_group(data, *group['original_span'])
        after = simulate_group(updated, *group['original_span'])
        assert len(before) == 1 and len(after) == len(group['pages'])
        for actual, expected in zip(after, group['pages']):
            assert actual['helper'] == before[0]['helper'] and actual['args'] == before[0]['args']
            assert actual['lines'] == [r['display_text'] for r in expected]
    # Excluded references are unchanged, including unresolved and runtime-name rows.
    new_code = {i['offset']: i for i in instructions(updated)}
    excluded_rows = {n for g in excluded for n in g['opening_rows']}
    for n in excluded_rows:
        for position in original[by_row[n]['id']]['reference_instructions']:
            assert at[position] == new_code[position]
    # Original choices, menu branches and prompts keep their code; only selected
    # text operands may change. No new IDs, jumps or menu behavior are introduced.
    changed_refs = {p for c in changes for p in c.get('reference_instructions', [])}
    layout_spans = [g['original_span'] for g in layouts]
    for position, inst in at.items():
        if position in changed_refs or any(a <= position < b for a,b in layout_spans):
            continue
        assert new_code[position] == inst
    assert len(selections) + len(excluded_rows) == 641
    report = {'schema_version': 1, 'version': '0.1.5', 'selected_rows': len(selections),
              'retained_japanese_rows_in_scope': len(excluded_rows), 'excluded_groups': excluded,
              'reflow_groups': len(layouts), 'additional_pages': sum(len(g['pages'])-1 for g in layouts),
              'decoded_script_bytes': len(updated), 'decoded_script_sha256': hashlib.sha256(updated).hexdigest(),
              'max_page_glyphs': max(sum(len(r['display_text']) for r in p) for g in layouts for p in g['pages']),
              'all_generated_pages_simulated': True, 'unchanged_branch_and_menu_code_verified': True,
              'excluded_source_references_unchanged': True, 'runtime_verified': False,
              'menu_layout_evidence': menu_evidence,
              'samples': [{'id': g['id'], 'text':g['text'], 'pages':[[r['text'] for r in p] for p in g['pages']]}
                          for g in layouts if any(n in g['source_offsets'] for n in [by_row[i]['source_offset'] for i in (109,121,158,398,610,639)])]}
    return selection, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    selection, report = prepare()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'selection':str(DEST), 'report':str(REPORT), **report}, ensure_ascii=False, indent=2))
    if args.write:
        if DEST.exists() or REPORT.exists():
            raise ValueError('Refusing to overwrite build inputs/evidence')
        DEST.write_text(json.dumps(selection, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
