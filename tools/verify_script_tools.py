"""Check script encoding and relocation without creating translated game assets."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import random
import struct
from script_repack import relocate_script
from script_strings import parse_pool
from sn3_archive import GameSource, ROOT
from sn3_codec import compress, decompress


def require_failure(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('Invalid input was accepted')


def roundtrip(raw, key):
    packed = compress(raw, key)
    decoded, used = decompress(packed, key)
    assert decoded == raw and used == len(packed)
    return len(packed)


def verify():
    index = json.loads((ROOT / 'work/translation/en/script_strings.index.json').read_text())
    rng = random.Random(50380)
    cases = [bytes([x]) for x in range(256)]
    cases += [b'A' * n for n in (2, 3, 17, 18, 255, 256, 257, 4096)]
    cases += [bytes(range(256)) * 4]
    cases += [bytes(rng.randrange(256) for _ in range(n)) for n in (7, 8, 9, 255, 256, 257, 4096)]
    # Repeated pairs separated by literals exercise nibble pairing across flags.
    cases += [b''.join(bytes((i, 255-i)) * 2 + b'xyz' for i in range(120))]
    for key in (0, 0x9831, 0xa695, 0xffff, 1):
        for raw in cases:
            roundtrip(raw, key)
    failures = 0
    for action in (lambda: compress(b''), lambda: compress(b'x', -1),
                   lambda: compress(b'x', 65536), lambda: compress(b'xx', max_input=1),
                   lambda: decompress(compress(b'test')[:-1]),
                   lambda: decompress(compress(b'test'), max_output=3)):
        require_failure(action)
        failures += 1
    stats = {'source_resources_checked': 0, 'compressed_originals_roundtripped': 0,
             'original_encoded_bytes': 0, 'reencoded_bytes': 0, 'decoded_bytes': 0,
             'relocated_resources_checked': 0, 'relocated_strings_checked': 0,
             'relocated_compressed_resources_roundtripped': 0}
    samples = []
    small_script = None
    with GameSource() as source:
        for resource in index['resources']:
            raw = source.read(resource['bank'], resource['offset'], resource['size'])
            assert hashlib.sha256(raw).hexdigest() == resource['sha256']
            compression = resource['compression']
            data = decompress(raw, int(compression['key'], 16))[0] if compression else raw
            parsed = parse_pool(data)
            stats['source_resources_checked'] += 1
            if compression:
                key = int(compression['key'], 16)
                packed_size = roundtrip(data, key)
                stats['compressed_originals_roundtripped'] += 1
                stats['decoded_bytes'] += len(data)
                stats['original_encoded_bytes'] += compression['encoded_bytes_consumed']
                stats['reencoded_bytes'] += packed_size
                if len(samples) < 3:
                    samples.append({'resource': resource['id'], 'decoded_size': len(data),
                                    'original_encoded_size': compression['encoded_bytes_consumed'],
                                    'reencoded_size': packed_size})
            if not parsed['strings']:
                continue
            if small_script is None:
                small_script = data
            chosen = {row['source_offset']: row for row in (parsed['strings'][0], parsed['strings'][-1])}
            targets = {offset: {'source_sha256': row['source_sha256'],
                                'text': 'Expanded dialogue relocation check. ' * 12}
                       for offset, row in chosen.items()}
            moved, changes = relocate_script(data, targets)
            assert len(moved) > len(data)
            assert moved[:32] == data[:32]
            assert moved[parsed['pool_offset']:len(data)] == data[parsed['pool_offset']:]
            for change in changes:
                assert change['new_offset'] >= len(data)
                actual = moved[change['new_offset']:].split(b'\0', 1)[0]
                assert actual.decode('cp932') == change['text']
            if compression:
                roundtrip(moved, key)
                stats['relocated_compressed_resources_roundtripped'] += 1
            stats['relocated_resources_checked'] += 1
            stats['relocated_strings_checked'] += len(changes)
    assert small_script is not None
    parsed = parse_pool(small_script)
    row = parsed['strings'][0]
    offset = row['source_offset']
    target = {'source_sha256': row['source_sha256'], 'text': 'Expanded offset check'}
    # Duplicate a real reference to exercise relocation of shared references.
    shared = bytearray(small_script)
    other_rows = [r for r in parsed['strings'][1:] if r['reference_instructions']]
    assert other_rows
    other_reference = other_rows[0]['reference_instructions'][0]
    word = row['pool_word_offset']
    struct.pack_into('<HH', shared, other_reference, 0x105 | ((word >> 16) << 12), word & 65535)
    moved_shared, shared_changes = relocate_script(shared, {offset: target})
    assert len(shared_changes[0]['reference_instructions']) >= 2
    # Append zero padding, then force the target past the old 16-bit boundary.
    expanded = small_script + bytes(max(0, parsed['pool_offset'] + 2 * 65536 - len(small_script)))
    long_result, long_changes = relocate_script(expanded, {offset: target})
    assert long_changes[0]['pool_word_offset'] > 65535
    no_op, no_changes = relocate_script(small_script, {})
    assert no_op == small_script and no_changes == []
    overflow = small_script + bytes(max(0, parsed['pool_offset'] + 2 * (1 << 20) - len(small_script)))
    for action in (lambda: relocate_script(small_script, {-1: target}),
                   lambda: relocate_script(small_script, {offset: dict(target, source_sha256='0' * 64)}),
                   lambda: relocate_script(small_script, {offset: dict(target, text='bad\0text')}),
                   lambda: relocate_script(small_script, {offset: dict(target, text='bad\ntext')}),
                   lambda: relocate_script(small_script, {offset: dict(target, text='\U0001f600')}),
                   lambda: relocate_script(overflow, {offset: target})):
        require_failure(action)
        failures += 1
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'source_iso_sha256': index['source_iso_sha256'], 'index_schema_version': index['schema_version'],
            'statistics': stats, 'synthetic_codec_roundtrips': len(cases) * 5,
            'invalid_inputs_rejected': failures, 'no_op_relocation_byte_identical': True,
            'shared_references_relocated': True, 'offset_above_65535_words_checked': True,
            'instruction_lengths_control_targets_and_original_pool_preserved': True,
            'samples': samples,
            'input_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                             ('tools/sn3_codec.py', 'tools/sn3_vm.py', 'tools/script_strings.py',
                              'tools/script_repack.py', 'tools/verify_script_tools.py',
                              'work/translation/en/script_strings.index.json')},
            'scope_limit': 'Static source-corpus and synthetic checks only. No runtime allocation, font, layout, command-token, or translated-playthrough acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = verify()
    destination = ROOT / 'docs/script_tools_validation.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'report': result}, indent=2), flush=True)
    if args.write:
        destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
