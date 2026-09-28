"""Integrate reviewed setup translations, then normalize glossary names; preview first."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import re
from sn3_archive import ROOT


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def collect():
    artifacts, merged = [], {}
    correction = None
    for stem in ('screenshot', 'related'):
        draft_path = 'work/translation/en/setup_ui.%s_drafts.json' % stem
        review_path = 'work/translation/en/setup_ui.%smeaning_review.json' % ('related_' if stem == 'related' else '')
        draft, review = read(draft_path), read(review_path)
        if sha(ROOT / draft_path) != review['target_sha256'] or review['required_fixes']:
            raise ValueError('Unreviewed draft revision or pending fixes: ' + draft_path)
        checks = {row['id']: row for row in review['records']}
        if set(checks) != {row['id'] for row in draft['entries']}:
            raise ValueError('Review coverage mismatch')
        artifacts.extend({'path': p, 'sha256': sha(ROOT / p)} for p in (draft_path, review_path))
        for original in draft['entries']:
            if original['id'] == 'name.convert':
                correction = {'removed_id': original['id'], 'replacement_id': 'name.kanji',
                              'reason': 'Native graphics and independent related review establish Kanji.'}
                continue
            entry = deepcopy(original)
            identity = entry.pop('id')
            target = entry.get('target_full')
            if identity in merged and merged[identity]['target_full'] != target:
                raise ValueError('Conflicting targets: ' + identity)
            item = merged.setdefault(identity, {'id': identity, 'target_full': target, 'source_records': [], 'reviews': []})
            item['source_records'].append({'artifact': draft_path, 'record': entry})
            item['reviews'].append({'artifact': review_path, **checks[identity]})
    auto_path = 'work/translation/en/setup_ui.auto_name_review.json'
    auto = read(auto_path)
    if auto['approved_shared_target'] != 'Auto-Name' or auto['status'] != 'auto_name_behavior_resolved_by_static_native_code':
        raise ValueError('Auto-Name behavior review is not approved')
    elf_path = ROOT / auto['source']['path']
    if sha(elf_path) != auto['source']['sha256']:
        raise ValueError('Auto-Name source changed')
    elf = elf_path.read_bytes()
    for evidence in auto['native_evidence']:
        raw = elf[int(evidence['file_offset_start'], 16):int(evidence['file_offset_end_exclusive'], 16)]
        if len(raw) != evidence['byte_length'] or hashlib.sha256(raw).hexdigest() != evidence['bytes_sha256']:
            raise ValueError('Auto-Name evidence range changed')
    artifacts.append({'path': auto_path, 'sha256': sha(ROOT / auto_path)})
    glossary_path = 'work/glossary/setup_ui.proposed.json'
    glossary = read(glossary_path)
    if sha(ROOT / glossary_path) != read('work/translation/en/setup_ui.meaning_review.json')['proposed_glossary_sha256']:
        raise ValueError('Glossary proposal changed after review')
    artifacts.append({'path': glossary_path, 'sha256': sha(ROOT / glossary_path)})
    glossary['status'] = 'accepted_for_setup_ui_after_independent_meaning_review'
    glossary['source_proposal'] = artifacts[-1]
    for entry in glossary['entries']:
        entry['prior_proposal_status'] = entry['status']
        entry['status'] = 'wiki_verified' if entry['status'] == 'wiki_verified_proposal' else 'project_translation_meaning_reviewed'
    glossary['do_not_touch'] = [row['target_name'] for row in glossary['entries']]
    replacements = {alias: row['target_name'] for row in glossary['entries'] for alias in row.get('aliases', [])}
    normalization = []
    for item in merged.values():
        results = {r['result'] for r in item['reviews']}
        if 'unresolved_tiny_text' in results or 'source_corroborated_target_pending' in results:
            item['meaning_status'] = 'unresolved'
            item['tentative_target'] = item['target_full']
            item['target_full'] = None
        elif results == {'preserve_existing_data'}:
            item['meaning_status'] = 'preserve_existing_data'
        else:
            item['meaning_status'] = 'meaning_reviewed'
        if 'auto' in item['id'] or item['id'] in ('name.footer', 'name.footer_short'):
            item['behavior_review'] = auto_path
        if item['target_full']:
            for alias, canonical in replacements.items():
                updated = re.sub(r'\b' + re.escape(alias) + r'\b', canonical, item['target_full'])
                if updated != item['target_full']:
                    normalization.append({'id': item['id'], 'before': item['target_full'], 'after': updated})
                    item['target_full'] = updated
        item['insertion_status'] = 'not_inserted_or_layout_validated'
    # Resolve transcription only. A researched canonical English monster name remains a separate queue item.
    merged['options.thumbnail.enemy_name_partial']['source_resolution'] = read('work/translation/en/setup_ui.related_meaning_review.json')['new_source_resolution']
    entries = list(merged.values())
    output = {'schema_version': 1, 'language': 'en', 'status': 'reviewed_translation_catalog_with_explicit_unresolved_thumbnail_text',
              'scope': 'Five screenshots and related setup/options native text; not every game interface.',
              'build_status': 'Not inserted. Latest playable ISO remains 0.1.4; next unused version is 0.1.5.',
              'inputs': artifacts, 'correction': correction,
              'normalization': {'order': 'Independent meaning reviews, source corrections, behavior resolution, then glossary normalization.',
                                'replacements': normalization, 'protected_terms': glossary['do_not_touch'],
                                'scope': 'All integrated target texts; source transcriptions and original review inputs are immutable.'},
              'statistics': {'records': len(entries), 'by_status': dict(Counter(r['meaning_status'] for r in entries)),
                             'distinct_reviewed_target_texts': len({r['target_full'] for r in entries if r['meaning_status'] == 'meaning_reviewed'})},
              'entries': entries,
              'release_gates': ['Translate native image pixels and encode/repack without damaging shared palettes or controls.',
                                'Relocate executable constants and verify all native consumers and encoding.',
                                'Measure runtime name expansion and UI text bounds; full-width dialogue encoding is not assumed safe here.',
                                'Build a new version and visually test every screen/state in PPSSPP.']}
    def target(key):
        return merged[key]['target_full']
    lines = ['# Setup and options: English translations', '',
             'The five supplied screenshots and related setup/options screens are translated below. These are reviewed text targets; they are **not yet inserted into the game**. The current test image remains 0.1.4.', '',
             '## 1. Options', '', '| Interface text | English |', '| --- | --- |']
    for key in ('options.title', 'options.bgm', 'options.voices', 'options.forecast', 'options.cursor', 'options.lr', 'common.confirm', 'options.exit'):
        lines.append('| ' + key.split('.')[-1].replace('_', ' ').title() + ' | ' + target(key) + ' |')
    lines += ['', 'Help text:', '']
    lines += ['- ' + target('options.' + key + '_help') for key in ('bgm', 'voices', 'forecast', 'cursor', 'lr')]
    lines += ['', 'Additional L/R settings: **Map Rotation** and **Unit Cycling**. Keep ON/OFF, Min/Max, and controller symbols.', '',
              '## 2. Protagonist selection', '', target('setup.select_prompt'), '', '○ Confirm. L/R changes the selection.', '',
              '## 3. Spirit affinity', '', '**Spirit Affinity**', '', target('description.spirit'), '',
              '## 4. Name entry', '', target('name.prompt'), '', '**Default names:** Rexx / Aty.', '',
              '**Controls:** Delete, Auto-Name, Confirm; L/R moves within the name.', '',
              '**Input tabs:** Hiragana, Katakana, Letters & Numbers, Symbols, Kanji.', '',
              'Auto-Name restores the protagonist’s default name. On the summon naming screen it cycles through preset names. The shared label is intentional; it does not mean random generation.', '',
              'The Japanese keyboard characters are input data, so they remain available. Choosing an English-first keyboard page is a separate implementation change.', '',
              '## 5. Name confirmation', '', 'Use the name "{name}"?', '', '**Yes / No**', '',
              'The screenshot example is “Use the name \\"Rexx\\"?” The actual prompt must retain the player’s chosen name.', '',
              '## Other related setup screens', '', target('select.affinity'), '', target('name.summon_heading'), '']
    for key in ('machine', 'yokai', 'beast'):
        lines += ['### ' + target('affinity.' + key) + ' Affinity', '', target('description.' + key), '']
    lines += ['## Review and implementation notes', '',
              '- The ambiguous tab is **Kanji**, verified from the original graphics.',
              '- Controller icons, arrows, existing English labels, numbers and runtime name insertion are preserved.',
              '- Six tiny regions within options-preview battle screenshots remain unreadable or tentative. One additional enemy label has a verified source reading but needs an English glossary decision.',
              '- Native source IDs, image rectangles, source hashes and original reviews are preserved in `work/translation/en/setup_ui.targets.json`.',
              '- Full descriptions have not been shortened to fit the original Japanese area. Layout and game testing remain required.', '',
              'Realm spellings follow the project’s [researched glossary](../work/glossary/setup_ui.json). The broader interface inventory and next translation batches are in [INTERFACE_TRANSLATION.md](INTERFACE_TRANSLATION.md).', '']
    return output, glossary, '\n'.join(lines).replace('\\"', '"')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    targets, glossary, document = collect()
    outputs = {'work/translation/en/setup_ui.targets.json': json.dumps(targets, ensure_ascii=False, indent=2) + '\n',
               'work/glossary/setup_ui.json': json.dumps(glossary, ensure_ascii=False, indent=2) + '\n',
               'docs/SETUP_UI_TRANSLATIONS.md': document}
    if any((ROOT / path).exists() for path in outputs):
        parser.error('Preserve existing outputs; use a new reviewed revision')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'outputs': list(outputs),
                      'statistics': targets['statistics'], 'correction': targets['correction'],
                      'normalization_changes': targets['normalization']['replacements'],
                      'sample_targets': [{k: r[k] for k in ('id', 'target_full', 'meaning_status')} for r in targets['entries'][:8]]}, indent=2))
    print(document[:1500])
    if args.write:
        for path, text in outputs.items():
            with (ROOT / path).open('x', encoding='utf-8') as stream:
                stream.write(text)


if __name__ == '__main__':
    main()
