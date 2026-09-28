"""Verify lossless pack reconstruction and relocation against the actual source."""
import argparse
from datetime import datetime, timezone
import json
import struct
from character_labels import collect
from sn3_archive import GameSource, ROOT, parse_index, child
from sn3_repack import repack, relocate_labels


def verify():
    inventory = json.loads((ROOT / 'docs/resource_inventory.json').read_text())
    targets = json.loads((ROOT / 'work/translation/en/character_labels.targets.json').read_text())['translations']
    containers = [node for node in inventory['nodes'] if node['kind'] in ('inline_pack', 'v4_pack')]
    counts = {'inline_pack': 0, 'v4_pack': 0}
    with GameSource() as source:
        for node in containers:
            data = source.read(node['bank'], node['offset'], node['size'])
            rebuilt = repack(data, {})
            if rebuilt != data:
                raise AssertionError('No-op rebuild changed ' + node['id'])
            counts[node['kind']] += 1
        data, _, entries = collect(source)
        translated, changes = relocate_labels(data, entries, targets)
        changed_fields = set()
        for change in changes:
            assert change['new_offset'] >= len(data)
            for field in change['pointer_fields']:
                pointer = struct.unpack_from('<I', translated, field)[0]
                assert pointer == change['new_offset']
                assert translated[pointer:].split(b'\0', 1)[0].decode('cp932') == change['text']
                changed_fields.update(range(field, field + 4))
        assert all(a == b or i in changed_fields for i, (a, b) in enumerate(zip(data, translated)))
        block = source.resource('01.DAT', 1)
        old_index = parse_index(block, len(block))
        grown = repack(block, {0: translated})
        new_index = parse_index(grown, len(grown))
        for i in range(1, old_index['count']):
            assert child(block, old_index, i) == child(grown, new_index, i)
        oversized = {k: dict(v) for k, v in targets.items()}
        first = next(iter(oversized))
        oversized[first]['text'] = 'Expanded text ' * 6000
        large_data, large_changes = relocate_labels(data, entries, oversized)
        assert any(c['new_offset'] > 65535 for c in large_changes)
        for change in large_changes:
            for field in change['pointer_fields']:
                assert struct.unpack_from('<I', large_data, field)[0] == change['new_offset']
        bad_hash = {first: dict(targets[first], source_sha256='0' * 64)}
        bad_nul = {first: dict(targets[first], text='bad\0label')}
        for invalid in (bad_hash, bad_nul):
            try:
                relocate_labels(data, entries, invalid)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid target was accepted')
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'source_iso_sha256': inventory['source_iso_sha256'],
            'byte_identical_noop_containers': counts,
            'relocated_labels_checked': len(changes),
            'shared_pointer_fields_checked': len(changed_fields) // 4,
            'unmodified_label_bytes_preserved': True,
            'unmodified_sibling_payloads_preserved': True,
            'relocation_beyond_65535_checked': True,
            'invalid_hash_and_nul_targets_rejected': True,
            'scope_limit': 'Static reconstruction checks only; no runtime allocation, font, layout, dialogue, or full-game coverage claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'report': result}, indent=2))
    if args.write:
        (ROOT / 'docs/repack_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
