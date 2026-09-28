"""Read-only resolver for the Chapter 4--8 source partitions.

The printed ``ordered_index`` is the stable, physical row index in the source
resource.  It is deliberately never renumbered after a shared prefix is
removed.  The program does not write source or translation data.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from sn3_archive import GameSource, ROOT
from sn3_codec import decompress


INDEX = ROOT / 'work/translation/en/script_strings.index.json'
MAIN_TAIL_START = {134: 1808, 157: 1808, 180: 3957, 203: 3957, 226: 3957}
COMMON_C6_C8_END = 3957

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load(number):
    catalog = json.loads(INDEX.read_text(encoding='utf-8'))
    resource = next(item for item in catalog['resources'] if item['id'] == '00:%05d' % number)
    with GameSource() as source:
        raw = source.resource(resource['bank'], resource['path'][0])
    assert digest(raw) == resource['sha256']
    data = decompress(raw, int(resource['compression']['key'], 16))[0] if resource['compression'] else raw
    if resource['compression']:
        assert digest(data) == resource['compression']['decoded_sha256']
    rows = sorted(resource['strings'], key=lambda row: min(row['reference_instructions']))
    for row in rows:
        text = data[row['source_offset']:row['source_offset'] + row['source_byte_length']]
        assert digest(text) == row['source_sha256']
    return resource, rows, data


def bounds(number, section, count):
    if section == 'all':
        return 0, count
    if section == 'main-tail':
        if number not in MAIN_TAIL_START:
            raise ValueError('main-tail is defined only for 134, 157, 180, 203, and 226')
        return MAIN_TAIL_START[number], count
    if section == 'common-c6-c8':
        if number not in (180, 203, 226):
            raise ValueError('common-c6-c8 is defined only for 180, 203, and 226')
        return 0, COMMON_C6_C8_END
    raise ValueError(section)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('resource', type=int)
    parser.add_argument('--section', choices=('all', 'main-tail', 'common-c6-c8'), default='all')
    parser.add_argument('--start', type=int, help='Physical ordered_index; defaults to the selected section start.')
    parser.add_argument('--count', type=int, default=80)
    parser.add_argument('--metadata', action='store_true', help='Print partition metadata only; no dialogue text.')
    args = parser.parse_args()
    resource, rows, data = load(args.resource)
    section_start, section_end = bounds(args.resource, args.section, len(rows))
    start = section_start if args.start is None else args.start
    if not section_start <= start <= section_end:
        raise ValueError('start is outside the selected section')
    end = min(start + args.count, section_end)
    metadata = {
        'resource': resource['id'], 'row_count': len(rows), 'section': args.section,
        'section_ordered_index_range': [section_start, section_end - 1],
        'emitted_ordered_index_range': [start, end - 1] if end > start else None,
        'source_sha256': resource['sha256'],
        'decoded_sha256': resource['compression'].get('decoded_sha256') if resource['compression'] else digest(data),
    }
    print(json.dumps(metadata, ensure_ascii=False))
    if args.metadata:
        return
    for index in range(start, end):
        row = rows[index]
        text = data[row['source_offset']:row['source_offset'] + row['source_byte_length']].decode('cp932')
        print(index, row['id'], row['reference_instructions'], text)


if __name__ == '__main__':
    main()
