"""Build a traceable interface translation queue from reviewed discovery metadata."""
import argparse
import hashlib
import json
from sn3_archive import ROOT


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def collect():
    paths = ['work/translation/en/interface.index.json',
             'work/translation/en/interface.executable_categories.json',
             'work/translation/en/setup_ui.targets.json',
             'work/translation/en/character_labels.index.json',
             'work/ui/interface_graphics.index.json',
             'work/ui/battle_assets/classification.json',
             'work/ui/menu_discovery/classification.json']
    inputs = [{'path': p, 'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest()} for p in paths]
    index, executable, setup, labels, graphics, island, menus = [read(p) for p in paths]
    if executable['source_index_sha256'] != inputs[0]['sha256']:
        raise ValueError('Executable categories refer to a different source index')
    batches = []
    for table in index['tables']:
        rows = table['strings']
        for number, start in enumerate(range(0, len(rows), 80)):
            end = min(start + 80, len(rows))
            chosen = rows[start:end]
            batches.append({'id': table['category'] + '_%03d' % number, 'table_id': table['id'],
                            'category': table['category'], 'row_ids': [r['id'] for r in chosen],
                            'context_before': [r['id'] for r in rows[max(0, start - 5):start]],
                            'context_after': [r['id'] for r in rows[end:end + 5]],
                            'status': 'awaiting_translation_and_independent_meaning_review',
                            'unverified_consumer_rows': [r['id'] for r in chosen if not r['references']],
                            'note': 'Read adjacent source and all record siblings. Boundaries are assignments, not proven display groups. Do not insert unverified consecutive-string fields independently.'})
    elf_rows = {r['id']: r for r in executable['entries']}
    if set(elf_rows) != {r['id'] for r in index['executable_literals']}:
        raise ValueError('Executable classification does not cover the candidate index exactly')
    output = {'schema_version': 1, 'language': 'en', 'requested_scope': 'all game interface text',
              'status': 'discovered_translation_and_audit_queue; full-game completeness not established',
              'inputs': inputs, 'table_batches': batches, 'executable_groups': executable['groups'],
              'graphics_queues': [paths[-2], paths[-1], 'work/translation/en/setup_ui.related_drafts.json'],
              'additional_queue': {'character_labels': paths[3], 'unclassified_native_graphics': paths[4],
                                   'scripts': 'work/translation/en/script_strings.index.json',
                                   'scripts_note': 'Story/dialogue pools are not automatically UI. Map actual menu/tutorial consumers before assigning interface work.'},
              'priority': ['Finish insertion and visual checks for reviewed setup/options targets',
                           'Shared confirmations, save/load and main menu controls',
                           'Battle commands, deployment, victory/defeat, status, equipment and item screens',
                           'Skills, summons, cooking, shop, tutorials/help and battle conditions',
                           'Island locations, night selection, gallery, minigames and appraisal',
                           'Resolve fallback/legacy text, boundary errors, palette variants and all remaining graphics'],
              'statistics': {'table_batches': len(batches), **index['statistics'],
                             'setup': setup['statistics'], 'executable_confidence': executable['counts']['confidence'],
                             'island_japanese_sprite_occurrences': island['coverage']['japanese_label_texture_count'],
                             'menu_japanese_sprite_occurrences': menus['counts']['japanese_text_sprites'],
                             'menu_latin_name_glossary_checks': menus['counts']['embedded_latin_name_sprites']},
              'counting_policy': 'These are source occurrences/candidates, not unique sentences or an additive total. Duplicates across tables, executable text, graphical states and scripts are not automatically merged.',
              'release_policy': 'Meaning review first, scripted glossary normalization second, measured layout and relocation/repacking third. Preserve control symbols, composed messages and dynamic names.'}
    doc = ['# All game interface: inventory and translation queue', '',
           'Scope confirmed by the user: **all game interface text**, including battle, inventory, status, tutorials, and save/load.', '',
           'The [five-screen translation](SETUP_UI_TRANSLATIONS.md) is consolidated with related setup/options variants. The catalog has **64 reviewed translation records (51 distinct English texts)**, six preserved English/numeric records and seven unresolved tiny-thumbnail records. All four summon affinities are included. These targets are not yet in an ISO.', '',
           '## Shared interface tables', '',
           'Found **3,633 source strings in 20 structurally bounded tables**, of which 3,619 contain Japanese. The same table pack is mirrored at `02:00003` and `00:00044/00007`; a future build must update both. Counts include repeated strings and fragments.', '',
           '| Category | Strings | Consumer still unverified |', '| --- | ---: | ---: |']
    for table in index['tables']:
        doc.append('| ' + table['category'].replace('_', ' ').capitalize() + ' | ' + str(len(table['strings'])) + ' | ' + str(sum(not r['references'] for r in table['strings'])) + ' |')
    doc += ['', 'There are 3,174 direct string-pointer references. Another 459 pool strings are retained with unresolved consumers, often adjacent to descriptive text. Adjacency alone does not prove ownership, number of lines or runtime access. The queue contains %d consecutive source batches, with context on both sides; none of these table batches has been translated in this pass.' % len(batches), '',
            '## Executable interface text', '',
            '**960 Japanese-bearing candidates** were individually inspected and classified into 108 adjacent semantic groups. 856 are likely user-facing, 71 are uncertain, and 33 are unlikely. These are semantic confidence ratings; native consumers have not been verified.', '',
            'Categories include main-menu and equipment help, save/load messages, battle commands and confirmations, inventory restrictions, status effects, shops, class changes, summon management, party abilities, gallery controls, minigame results, and fishing. The queue keeps 25 appraisal-service dialogue lines separate for contextual translation.', '',
            'Three candidates contain leading binary bytes and require corrected boundaries: voice playback, the save title, and battle selection. Twenty-nine suspected false positives and 11 fallback/legacy labels remain in the audit queue. The current executable scan omits English-only strings and standalone punctuation; they must be recovered when reconstructing complete messages.', '',
            '## Text inside graphics', '',
            '| Source family | Discovery result |', '| --- | --- |',
            '| Setup/options, packs 28–33 | 410 decoded textures classified; 92 carry text, with 122 mapped translation-record occurrences. Keyboard characters, controls and artwork are tracked separately. |',
            '| Island/location selection, packs 35–36 | 520 decoded textures examined; 12 Japanese label occurrences, representing six unique images. Directory `battle_assets` is provisional and does not mean battle-only use. |',
            '| Night selection, battle preparation/selection, gallery, appraisal | 368 sprites classified; 41 Japanese text sprites and 38 Latin-name portraits queued for glossary consistency. Six gallery sprites still need decoding. |',
            '| Full existing static-texture inventory | 7,263 signatures inspected; 7,262 bounded resources, grouped into 3,729 distinct payloads containing 16,400 sprites. These include art, effects, animations and font data; they are **not** 16,400 texts. |', '',
            'Selected graphics were decoded to source PNGs with stable IDs, source/image hashes, dimensions and texture-storage offsets. Text regions have inspection rectangles. They are not replacement masks or proven in-game limits.', '',
            '## Remaining discovery and implementation', '',
            'Full interface coverage is not yet proven. Remaining work includes compressed graphics outside the selected packs, unsupported palette/texture formats, nested resources and layout consumers, script-driven tutorial/menu text, complete message assembly, and navigation through all game states. Character names and titles also use the existing character-label index.', '',
            'For the next playable version, begin with the reviewed setup/options targets: relocate executable literals, translate and repack native image text, preserve the keyboard/controller data, then check both protagonists, all affinities, name confirmation, and every options state. The separate dialogue font fix is not evidence that these UI renderers support the same encoding or spacing.', '',
            'The latest playable build remains **0.1.4**. The next unused version is **0.1.5**. No UI translation is claimed inserted, and the running game was not changed.', '',
            '## Reproducible artifacts', '',
            '- `work/translation/en/setup_ui.targets.json`: reviewed targets with immutable draft/review provenance.',
            '- `work/translation/en/interface.index.json`: source hashes, offsets, categories and references; Japanese text resolved locally.',
            '- `work/translation/en/interface.executable_categories.json`: candidate-by-candidate semantic classification.',
            '- `work/translation/en/interface.queue.json`: translation batches, context IDs and audit queues.',
            '- `work/ui/interface_graphics.index.json`: bounded source graphics and duplicate-resource identities.',
            '- `work/ui/user_setup_screenshots/index.json`: original screenshots and measured inspection regions.',
            '- `work/ui/battle_assets/classification.json` and `work/ui/menu_discovery/classification.json`: visual text classification and gaps.', '',
            'Source Japanese dialogue was not exported. Short UI labels and small UI descriptions are retained where needed for review. Prior drafts, reviews, build inputs and game images are preserved.', '']
    return output, '\n'.join(doc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    queue, document = collect()
    outputs = {'work/translation/en/interface.queue.json': json.dumps(queue, indent=2) + '\n',
               'docs/INTERFACE_TRANSLATION.md': document}
    if any((ROOT / path).exists() for path in outputs):
        parser.error('Preserve existing queue revision')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'outputs': list(outputs),
                      'statistics': queue['statistics'], 'sample_batch': queue['table_batches'][0]}, indent=2))
    print(document[:1800])
    if args.write:
        for path, text in outputs.items():
            with (ROOT / path).open('x', encoding='utf-8') as stream:
                stream.write(text)


if __name__ == '__main__':
    main()
