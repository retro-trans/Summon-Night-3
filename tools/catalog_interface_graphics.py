"""Catalog every recognized static texture resource; text classification remains explicit."""
import argparse
from collections import Counter
import hashlib
import json
from sn3_archive import ROOT, GameSource
from sn3_ui_textures import texture_records


def sha(data):
    return hashlib.sha256(data).hexdigest()


def collect():
    inventory = json.loads((ROOT / 'docs/resource_inventory.json').read_text())
    groups, rejected = {}, []
    with GameSource() as source:
        for node in inventory['nodes']:
            if not node.get('header_hex', '').startswith('0100000001112100'):
                continue
            identity = {key: node[key] for key in ('id', 'bank', 'path', 'offset', 'size', 'sha256')}
            if node['sha256'] in groups:
                groups[node['sha256']]['occurrences'].append(identity)
                continue
            data = source.read(node['bank'], node['offset'], node['size'])
            if sha(data) != node['sha256']:
                raise ValueError('Source resource hash changed: ' + node['id'])
            try:
                rows = texture_records(data)
            except ValueError as exc:
                rejected.append({'source': identity, 'reason': str(exc)})
                continue
            for row in rows:
                row['priority_hint'] = 'wide_short_sprite' if row['width'] >= 48 and row['height'] <= 64 else 'other_sprite'
                row['pixel_storage_sha256'] = sha(data[row['data_offset']:row['data_offset'] + row['data_size']])
            groups[node['sha256']] = {'source_sha256': node['sha256'], 'occurrences': [identity],
                                      'classification': 'not_visually_classified', 'textures': rows}
    exports = []
    for name in ('setup_assets_complete', 'battle_assets', 'menu_discovery'):
        path = ROOT / 'work/ui' / name / 'index.json'
        if not path.exists():
            continue
        index = json.loads(path.read_text())
        exports.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes()),
                        'decoded_textures': len(index['textures']), 'skipped_records': len(index['skipped']),
                        'resources': index['resources'], 'classification_file': ('work/ui/' + name + '/classification.json')
                        if (path.parent / 'classification.json').exists() else None})
    values = list(groups.values())
    return {'schema_version': 1, 'source_iso_sha256': inventory['source_iso_sha256'],
            'scope': 'All static texture signatures in the existing recursive source inventory, plus separately decoded selected UI packs.',
            'interpretation': 'Resource/sprite counts are not text counts. Fonts, artwork, animation and UI are included. Shape hints prioritize inspection and never exclude other images.',
            'statistics': {'signature_resources': sum(len(g['occurrences']) for g in values) + len(rejected),
                           'bounded_resources': sum(len(g['occurrences']) for g in values),
                           'unique_resource_payloads': len(values),
                           'sprites_in_unique_payloads': sum(len(g['textures']) for g in values),
                           'wide_short_sprites_in_unique_payloads': sum(r['priority_hint'] == 'wide_short_sprite' for g in values for r in g['textures']),
                           'rejected_resources': len(rejected)},
            'resources': values, 'rejected': rejected, 'decoded_exports': exports,
            'coverage_gaps': ['Compressed graphics outside the selected exported packs remain undiscovered.',
                              'Other resource formats, palette variants and nested compressed payloads need decoding.',
                              'Visual text classification of the catalog is incomplete; in-game navigation is required to prove coverage.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'work/ui/interface_graphics.index.json'
    if args.write and path.exists():
        parser.error('Preserve existing catalog; choose a new revision in code')
    report = collect()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(path),
                      'statistics': report['statistics'],
                      'samples': [{'occurrences': g['occurrences'][:2], 'texture_count': len(g['textures']),
                                   'sample_sprite': g['textures'][0]} for g in report['resources'][:2]],
                      'exports': [r['path'] for r in report['decoded_exports']]}, indent=2))
    if args.write:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
