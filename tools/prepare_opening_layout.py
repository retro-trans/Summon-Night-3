"""Select complete independently reviewed opening groups; preview before writing."""
import argparse
import hashlib
import json

from dialogue_layout import PROFILE, PIXEL_PROFILE, layout_dialogue
from sn3_archive import GameSource, ROOT
from sn3_codec import decompress


def prepare(profile=PROFILE):
    target_path = ROOT / 'work/translation/en/opening_000.targets.json'
    review_path = ROOT / 'work/translation/en/opening_000.meaning_review.json'
    drafts = json.loads(target_path.read_text(encoding='utf-8'))
    review = json.loads(review_path.read_text(encoding='utf-8'))
    if (not review['independent_review'] or
            review['reviewed_target_sha256'] != hashlib.sha256(target_path.read_bytes()).hexdigest() or
            review['required_meaning_edits']):
        raise ValueError('Opening review provenance or meaning acceptance is invalid')
    translations, groups = {}, {}
    for identity, row in drafts['translations'].items():
        # Group 43 crosses into the next assignment; do not insert a fragment.
        if row['slice_row'] >= 78:
            continue
        if not row['text']:
            raise ValueError('Selected opening row has no draft')
        translations[identity] = {key: row[key] for key in ('source_sha256', 'text', 'source_offset')}
        translations[identity].update(status='meaning_reviewed', encoding_profile='dialogue_fullwidth_cp932')
        # Groups 36-39 form a conditional choice queue. Preserve original code.
        if row['sentence_group'] not in (36, 37, 38, 39):
            groups.setdefault(row['sentence_group'], []).append(row['source_offset'])
    selection = {'schema_version': 1, 'language': 'en', 'resource_id': '00:00065',
                 'source_iso_sha256': '00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda',
                 'scope': '78 reviewed opening rows in complete display groups, including three choices; boundary group excluded.',
                 'reviewed_by': '/root/review_opening_meaning', 'layout_profile': profile,
                 'review_inputs_sha256': {str(path.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(path.read_bytes()).hexdigest()
                                         for path in (target_path, review_path)},
                 'layout_groups': [{'id': 'opening_000:group:%d' % group, 'source_offsets': offsets}
                                   for group, offsets in groups.items()],
                 'translations': translations}
    if profile == PIXEL_PROFILE:
        from font_patch import PROFILE as FONT_PROFILE, FONT_POOL_CAPACITY
        selection['required_font_profile'] = FONT_PROFILE
        selection['required_font_pool_capacity'] = FONT_POOL_CAPACITY
    with GameSource() as source:
        data = decompress(source.resource('00.DAT', 65), 0xa695)[0]
    updated, changes, layouts = layout_dialogue(data, {t['source_offset']: t for t in translations.values()}, selection['layout_groups'], profile)
    preview = {'selected_rows': len(changes), 'reflowed_groups': len(layouts),
               'required_font_profile': selection.get('required_font_profile'),
               'required_font_pool_capacity': selection.get('required_font_pool_capacity'),
               'additional_pages': sum(len(g['pages']) - 1 for g in layouts),
               'old_decoded_bytes': len(data), 'new_decoded_bytes': len(updated),
               'decoded_sha256': hashlib.sha256(updated).hexdigest(),
               'samples': [{'id': g['id'], 'text': g['text'],
                            'pages': [[r['text'] for r in page] for page in g['pages']]}
                           for g in layouts[:5]],
               'scope_limit': 'Static preview only; the selected font/layout profile and pagination need in-game verification.'}
    return selection, preview


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--profile', choices=[PROFILE, PIXEL_PROFILE], default=PROFILE)
    args = parser.parse_args()
    selection, preview = prepare(args.profile)
    destination = ROOT / 'work/translation/en' / ('opening_latin_pool192.targets.json' if args.profile == PIXEL_PROFILE else 'opening_layout.targets.json')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'preview': preview}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(selection, output, ensure_ascii=False, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
