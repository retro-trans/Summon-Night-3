"""Index verified CP932 pools in recognized script headers, without transcripts."""
import argparse
from collections import Counter
import hashlib
import json
import re
import struct
from sn3_archive import GameSource, ROOT
from sn3_codec import decoded_size, decompress
from sn3_vm import verify_script

SCRIPT_PREFIX = bytes.fromhex('010000000102000000100102')
JAPANESE = re.compile('[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]')


def parse_pool(data):
    if len(data) < 32 or data[:12] != SCRIPT_PREFIX:
        raise ValueError('Unrecognized script header')
    variant, entry_word, pool_word, reserved1, reserved2 = struct.unpack_from('<5I', data, 12)
    if variant not in (0x1010, 0x1020) or reserved1 or reserved2:
        raise ValueError('Unrecognized script variant')
    pool = pool_word * 2
    if not 32 <= pool < len(data) or data[pool:pool + 2] != b'\0\0':
        raise ValueError('Invalid script string pool')
    rows = []
    cursor = pool
    while cursor < len(data):
        if data[cursor] == 0:
            cursor += 1
            continue
        if cursor % 2:
            raise ValueError('Unaligned script string')
        end = data.index(b'\0', cursor)
        raw = data[cursor:end]
        text = raw.decode('cp932', 'strict')
        if any(b < 32 for b in raw):
            raise ValueError('Control bytes need explicit parsing before indexing')
        rows.append({'source_offset': cursor, 'pool_word_offset': (cursor - pool) // 2,
                     'source_byte_length': len(raw), 'source_sha256': hashlib.sha256(raw).hexdigest(),
                     'contains_japanese': bool(JAPANESE.search(text))})
        cursor = end + 1
    verified = verify_script(data, rows)
    for row in rows:
        row['reference_instructions'] = verified['references'][row['pool_word_offset']]
    return {'variant': hex(variant), 'entry_word': entry_word, 'pool_offset': pool,
            'vm_statistics': {k: v for k, v in verified.items() if k != 'references'}, 'strings': rows}


def collect_scripts(source):
    inventory = json.loads((ROOT / 'docs/resource_inventory.json').read_text())
    resources = []
    for node in inventory['nodes']:
        compression = None
        direct = node.get('header_hex', '').startswith(SCRIPT_PREFIX.hex())
        # The executable uses 0xa695 for the story script loader. Probe only
        # undecoded leaves; require both bounded decompression and the exact
        # script signature before accepting a result.
        if not direct and node['kind'] != 'unclassified':
            continue
        data = source.read(node['bank'], node['offset'], node['size'])
        if hashlib.sha256(data).hexdigest() != node['sha256']:
            raise ValueError('Resource hash mismatch: ' + node['id'])
        if not direct:
            try:
                if not 32 <= decoded_size(data, 0xa695) <= 8 * 1024 * 1024:
                    continue
                decoded, consumed = decompress(data, 0xa695, 8 * 1024 * 1024)
            except ValueError:
                continue
            if not decoded.startswith(SCRIPT_PREFIX):
                continue
            if any(data[consumed:]):
                raise ValueError('Nonzero compressed script tail: ' + node['id'])
            compression = {'key': '0xa695', 'encoded_bytes_consumed': consumed,
                           'decoded_size': len(decoded), 'decoded_sha256': hashlib.sha256(decoded).hexdigest()}
            data = decoded
        parsed = parse_pool(data)
        resource = {key: node[key] for key in ('id', 'bank', 'path', 'offset', 'size', 'sha256')}
        resource.update(parsed)
        resource['compression'] = compression
        resource['string_offset_space'] = 'decoded_resource' if compression else 'raw_resource'
        for row in resource['strings']:
            row['id'] = '%s:text:%08x' % (node['id'], row['source_offset'])
        resources.append(resource)
    rows = [row for resource in resources for row in resource['strings']]
    unique = {row['source_sha256'] for row in rows}
    unique_japanese = {row['source_sha256'] for row in rows if row['contains_japanese']}
    vm_totals = Counter()
    for resource in resources:
        vm_totals.update(resource['vm_statistics'])
    return {'schema_version': 2, 'source_iso_sha256': source.manifest['source']['iso_sha256'],
            'scope': 'Recognized script string pools only. Occurrences are distinct translation contexts.',
            'reinsertion_ready': False,
            'reference_status': 'Verified instruction byte offsets in the decoded resource; 20-bit pool-word operands.',
            'statistics': {'script_resources': len(resources), 'variants': dict(Counter(r['variant'] for r in resources)),
                           'compressed_script_resources': sum(r['compression'] is not None for r in resources),
                           'resources_with_strings': sum(bool(r['strings']) for r in resources),
                           'string_occurrences': len(rows),
                           'japanese_occurrences': sum(row['contains_japanese'] for row in rows),
                           'unique_source_strings': len(unique), 'unique_japanese_strings': len(unique_japanese),
                           'occurrences_without_reference': sum(not row['reference_instructions'] for row in rows),
                           'vm': dict(vm_totals)},
            'resources': resources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with GameSource() as source:
        report = collect_scripts(source)
    destination = ROOT / 'work/translation/en/script_strings.index.json'
    examples = []
    for resource in report['resources']:
        if resource['strings']:
            examples.append({'resource': resource['id'], 'pool_offset': resource['pool_offset'],
                             'first_string': resource['strings'][0]})
        if len(examples) == 3:
            break
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'statistics': report['statistics'], 'sample_metadata': examples,
                      'reinsertion_ready': False}, indent=2))
    if args.write:
        destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
