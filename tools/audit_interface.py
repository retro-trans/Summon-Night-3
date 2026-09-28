"""Verify UI catalogs against source bytes, immutable reviews, images and queue coverage."""
import argparse
from collections import Counter
import hashlib
import json
from sn3_archive import ROOT
from index_interface import collect as collect_strings
from prepare_setup_ui import collect as collect_targets


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    from PIL import Image
    checks = []
    def check(name, actual, expected):
        if actual != expected:
            raise ValueError('%s: actual %r, expected %r' % (name, actual, expected))
        checks.append({'check': name, 'passed': True})
    index = read('work/translation/en/interface.index.json')
    check('String catalog regenerated from original archive and executable', collect_strings(), index)
    expected_targets, expected_glossary, document = collect_targets()
    check('Targets regenerated after immutable meaning and behavior reviews', read('work/translation/en/setup_ui.targets.json'), expected_targets)
    check('Accepted UI glossary regeneration', read('work/glossary/setup_ui.json'), expected_glossary)
    check('Readable translations match reviewed targets', (ROOT / 'docs/SETUP_UI_TRANSLATIONS.md').read_text(encoding='utf-8'), document)
    queue = read('work/translation/en/interface.queue.json')
    for row in queue['inputs']:
        check('Queue input hash: ' + row['path'], digest(ROOT / row['path']), row['sha256'])
    expected_ids = [r['id'] for table in index['tables'] for r in table['strings']]
    assigned = [identity for batch in queue['table_batches'] for identity in batch['row_ids']]
    check('Every table string assigned exactly once', Counter(assigned), Counter(expected_ids))
    check('Bounded source batches', all(0 < len(b['row_ids']) <= 80 for b in queue['table_batches']), True)
    check('Runtime name composition preserved', next(r for r in expected_targets['entries'] if r['id'] == 'name.confirm_prompt')['source_records'][0]['record']['target_composition'][1]['kind'], 'runtime_name')
    check('Incorrect Convert target removed', any(r['id'] == 'name.convert' for r in expected_targets['entries']), False)
    check('Kanji correction present', next(r['target_full'] for r in expected_targets['entries'] if r['id'] == 'name.kanji'), 'Kanji')
    images = 0
    for directory in ('setup_assets_complete', 'battle_assets', 'menu_discovery'):
        path = ROOT / 'work/ui' / directory
        texture_index = json.loads((path / 'index.json').read_text())
        for row in texture_index['textures']:
            image_path = path / row['image_file']
            if digest(image_path) != row['image_sha256']:
                raise ValueError('Image hash mismatch: ' + str(image_path))
            with Image.open(image_path) as image:
                if image.size != (row['width'], row['height']):
                    raise ValueError('Image dimensions mismatch')
            images += 1
        check('All exported image hashes/dimensions: ' + directory, True, True)
    screenshots = read('work/ui/user_setup_screenshots/index.json')
    for row in screenshots['screenshots']:
        path = ROOT / 'work/ui/user_setup_screenshots' / row['image_file']
        check('Original screenshot preserved: ' + row['screen'], digest(path), row['sha256'])
        check('Screenshot rectangles bounded: ' + row['screen'], all(0 <= x < x + w <= row['width'] and 0 <= y < y + h <= row['height'] for x, y, w, h in (r['rect'] for r in row['regions'])), True)
    # Source transcriptions are independently bound to the original executable, including punctuation fragments.
    elf = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    fragments = 0
    for entry in read('work/translation/en/setup_ui.screenshot_drafts.json')['entries']:
        for source in entry.get('binary_sources', []):
            offset = int(source['file_offset'], 16)
            check('Executable UI fragment: ' + entry['id'] + ':' + source['file_offset'], elf[offset:elf.index(b'\0', offset)].decode('cp932'), source['source_exact'])
            fragments += 1
    return {'schema_version': 1, 'checked_on': '2026-09-26', 'passed': True,
            'scope': 'Source catalogs, review provenance, glossary, preserved images, runtime-placeholder metadata and queue integrity. No in-game layout or insertion acceptance.',
            'statistics': {'checks': len(checks), 'table_strings': len(expected_ids), 'executable_candidates': len(index['executable_literals']),
                           'exported_images_hash_and_dimension_checked': images, 'screenshots': len(screenshots['screenshots']),
                           'exact_executable_source_fragments': fragments}, 'checks': checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'docs/interface_audit_2026-09-26.json'
    if args.write and path.exists():
        parser.error('Do not overwrite prior validation evidence')
    report = audit()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(path),
                      'statistics': report['statistics'], 'sample_checks': report['checks'][:5], 'passed': report['passed']}, indent=2))
    if args.write:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
