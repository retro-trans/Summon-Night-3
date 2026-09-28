"""Read Summon Night 3 PSP resource indexes without exporting source scripts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]


def parse_index(data, payload_size=None, allow_external=False):
    if len(data) < 8:
        raise ValueError('Index too short')
    count, tag, shift, bias = struct.unpack_from('<4H', data)
    if tag != 1 or shift > 16 or not count or 8 + count * 8 > len(data):
        raise ValueError('Not a supported resource index')
    if bias and not allow_external:
        raise ValueError('External index requires a separate payload')
    unit = 1 << shift
    rows = []
    previous_end = None
    for i in range(count):
        offset, size = struct.unpack_from('<II', data, 8 + i * 8)
        byte_offset, byte_size = (offset - bias) * unit, size * unit
        if byte_offset < 0:
            raise ValueError('Negative resource offset')
        if payload_size is not None and byte_offset + byte_size > payload_size:
            raise ValueError('Resource exceeds payload size')
        if previous_end is not None and offset != previous_end:
            raise ValueError('Noncontiguous resource index')
        previous_end = offset + size
        rows.append({'id': i, 'offset': byte_offset, 'size': byte_size})
    if not bias and rows[0]['offset'] < 8 + count * 8:
        raise ValueError('Payload overlaps its index')
    return {'count': count, 'tag': tag, 'shift': shift, 'unit_bytes': unit,
            'bias_units': bias, 'table_bytes': 8 + count * 8, 'entries': rows,
            'indexed_end': rows[-1]['offset'] + rows[-1]['size']}


def child(data, index, number):
    entry = index['entries'][number]
    return data[entry['offset']:entry['offset'] + entry['size']]


def parse_v4(data):
    if len(data) < 40:
        raise ValueError('V4 container too short')
    version, reserved, name_count, names_offset, count, table_offset, *tail = struct.unpack_from('<10I', data)
    if version != 0x40000 or reserved or any(tail) or not count or count > 65535:
        raise ValueError('Not a supported V4 container')
    if name_count > count or table_offset < 40 or table_offset + count * 8 > len(data):
        raise ValueError('Invalid V4 table bounds')
    names = {}
    if name_count:
        if names_offset < 40 or names_offset + name_count * 20 > table_offset:
            raise ValueError('Invalid V4 name table')
        for i in range(name_count):
            pos = names_offset + i * 20
            key = struct.unpack_from('<I', data, pos + 16)[0]
            number = key >> 16
            if number >= count:
                raise ValueError('V4 name references missing entry')
            names[number] = data[pos:pos + 16].split(b'\0', 1)[0].decode('ascii', 'replace')
    rows = []
    previous_end = None
    for i in range(count):
        pos = table_offset + i * 8
        offset = int.from_bytes(data[pos:pos + 3], 'big') * 16
        size = int.from_bytes(data[pos + 3:pos + 6], 'big') * 16
        empty = offset == 0 and size == 0
        if not empty and (offset < table_offset + count * 8 or offset + size > len(data)):
            raise ValueError('Invalid V4 entry bounds')
        if not empty and previous_end is not None and offset != previous_end:
            raise ValueError('Noncontiguous V4 entries')
        if not empty:
            previous_end = offset + size
        rows.append({'id': i, 'offset': offset, 'size': size,
                     'flags_hex': data[pos + 6:pos + 8].hex(), 'name': names.get(i)})
    return {'count': count, 'unit_bytes': 16, 'entries': rows,
            'indexed_end': previous_end, 'kind': 'v4_pack', 'table_offset': table_offset}


class GameSource:
    def __init__(self, iso_path=None):
        self.manifest = json.loads((ROOT / 'docs/source_scan.json').read_text())
        self.files = {Path(row['path']).name: row for row in self.manifest['files']
                      if '/USRDIR/' in row['path']}
        self.stream = (Path(iso_path) if iso_path else ROOT / 'work/source/original.iso').open('rb')
        actual_size = self.stream.seek(0, 2)
        if iso_path:
            from scan_source import inventory
            _, actual_files = inventory(self.stream, actual_size)
            self.files = {Path(row['path']).name: row for row in actual_files if '/USRDIR/' in row['path']}
        elif actual_size != self.manifest['source']['iso_size_bytes']:
            self.stream.close()
            raise ValueError('Unexpected working ISO length')
        header = self.read('00.DAT', 0, 8)
        count = struct.unpack_from('<H', header)[0]
        table = self.read('00.DAT', 0, 8 + count * 8)
        self.indexes = {'00.DAT': parse_index(table, self.files['00.DAT']['size_bytes'])}
        self.index_locations = {'00.DAT': {'bank': '00.DAT', 'offset': 0, 'size': len(table)}}
        master_entry = self.indexes['00.DAT']['entries'][44]
        master = self.read('00.DAT', master_entry['offset'], master_entry['size'])
        master_index = parse_index(master, len(master))
        for number, bank in enumerate(['01.DAT', '02.DAT', '03.DAT']):
            entry = master_index['entries'][number]
            self.indexes[bank] = parse_index(child(master, master_index, number),
                                             self.files[bank]['size_bytes'], True)
            self.index_locations[bank] = {'bank': '00.DAT',
                                          'offset': master_entry['offset'] + entry['offset'],
                                          'size': entry['size']}
        voices_entry = master_index['entries'][3]
        voices = child(master, master_index, 3)
        voice_index = parse_index(voices, len(voices))
        if voice_index['count'] != 19:
            raise ValueError('Unexpected voice-bank index count')
        for number in range(19):
            bank = 'SV%02d.DAT' % number
            entry = voice_index['entries'][number]
            self.indexes[bank] = parse_index(child(voices, voice_index, number),
                                             self.files[bank]['size_bytes'], True)
            self.index_locations[bank] = {'bank': '00.DAT',
                                          'offset': master_entry['offset'] + voices_entry['offset'] + entry['offset'],
                                          'size': entry['size']}
        for bank, index in self.indexes.items():
            if index['indexed_end'] != self.files[bank]['size_bytes']:
                raise ValueError('Index does not account for full bank: ' + bank)

    def read(self, bank, offset, size):
        entry = self.files[bank]
        if offset < 0 or size < 0 or offset + size > entry['size_bytes']:
            raise ValueError('Bank read out of bounds')
        self.stream.seek(entry['sector'] * 2048 + offset)
        data = self.stream.read(size)
        if len(data) != size:
            raise ValueError('Short bank read')
        return data

    def resource(self, bank, number):
        entry = self.indexes[bank]['entries'][number]
        return self.read(bank, entry['offset'], entry['size'])

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stream.close()


def signature(data):
    for marker, label in [(b'RIFF', 'riff_audio'), (b'PSMF', 'video'),
                          (b'PPHD', 'sound_bank'), (b'PPPG', 'sound_program'),
                          (b'MIG.', 'gim_texture'), (b'TIM2', 'tim2_texture')]:
        if data.startswith(marker):
            return label
    if not any(data):
        return 'zero_filled'
    return 'unclassified'


def walk_resource(data, bank, path, offset, depth=0, name=None):
    if depth > 12:
        raise ValueError('Resource nesting exceeds expected depth')
    node = {'id': bank[:-4] + ':' + '/'.join('%05d' % p for p in path),
            'bank': bank, 'path': path, 'offset': offset, 'size': len(data)}
    if name:
        node['name'] = name
    try:
        index = parse_index(data, len(data))
    except ValueError:
        try:
            index = parse_v4(data)
        except ValueError:
            index = None
    if index:
        node.update({'kind': index.get('kind', 'inline_pack'), 'count': index['count'],
                     'unit_bytes': index['unit_bytes'], 'indexed_end': index['indexed_end']})
        yield node
        for entry in index['entries']:
            if entry['size']:
                yield from walk_resource(child(data, index, entry['id']), bank,
                                         path + [entry['id']], offset + entry['offset'], depth + 1, entry.get('name'))
    else:
        kind = signature(data)
        try:
            external = parse_index(data, allow_external=True)
            if external['bias_units']:
                kind = 'external_index'
        except ValueError:
            pass
        node.update({'kind': kind, 'sha256': hashlib.sha256(data).hexdigest(),
                     'header_hex': data[:16].hex()})
        yield node


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--compact', action='store_true')
    args = parser.parse_args()
    with GameSource() as source:
        banks = []
        nodes = []
        for bank, index in source.indexes.items():
            banks.append({'bank': bank, 'index_location': source.index_locations[bank],
                          'count': index['count'], 'nonempty_count': sum(bool(row['size']) for row in index['entries']),
                          'unit_bytes': index['unit_bytes'], 'bias_units': index['bias_units'],
                          'indexed_end': index['indexed_end'], 'entries': index['entries']})
            if bank.startswith('SV') or bank == '03.DAT':
                continue
            for entry in index['entries']:
                if entry['size']:
                    nodes.extend(walk_resource(source.resource(bank, entry['id']), bank,
                                               [entry['id']], entry['offset']))
        report = {'schema_version': 1, 'source_iso_sha256': source.manifest['source']['iso_sha256'],
                  'scope': 'All 23 resource indexes; recursive payload inventory for 00/01/02. No text exported.',
                  'banks': banks, 'nodes': nodes}
    kinds = Counter(node['kind'] for node in nodes)
    print(json.dumps({'mode': 'write' if args.write else 'dry run',
                      'report': str(ROOT / 'docs/resource_inventory.json'),
                      'banks': len(banks) if args.compact else [{k: v for k, v in bank.items() if k != 'entries'} for bank in banks],
                      'node_count': len(nodes), 'kinds': dict(kinds),
                      'sample_nodes': nodes[:3]}, indent=2))
    if args.write:
        (ROOT / 'docs/resource_inventory.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
