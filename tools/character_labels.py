"""Index character/class labels; source text is resolved from the local ISO."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from sn3_archive import GameSource, ROOT, parse_index, child


def collect(source):
    block = source.resource('01.DAT', 1)
    index = parse_index(block, len(block))
    labels = child(block, index, 0)
    master = source.resource('00.DAT', 44)
    master_index = parse_index(master, len(master))
    cached = child(master, master_index, 6)
    cached_index = parse_index(cached, len(cached))
    if labels != child(cached, cached_index, 0):
        raise ValueError('Resident and bank character label tables differ')
    count = struct.unpack_from('<I', labels)[0]
    pool_start = 4 + count * 32
    strings = {}
    for row in range(count):
        fields = struct.unpack_from('<8I', labels, 4 + row * 32)
        for slot, pointer in enumerate(fields[1:], 1):
            if not pointer:
                continue
            if not pool_start <= pointer < len(labels):
                raise ValueError('Character string pointer out of bounds')
            end = labels.index(b'\0', pointer)
            raw = labels[pointer:end]
            text = raw.decode('cp932')
            entry = strings.setdefault(pointer, {
                'id': 'char_label:%08x' % pointer,
                'source_offset': pointer,
                'source_byte_length': len(raw),
                'source_sha256': hashlib.sha256(raw).hexdigest(),
                'contains_japanese': any('\u3040' <= c <= '\u9fff' or '\uff66' <= c <= '\uff9f' for c in text),
                'references': [],
            })
            entry['references'].append({'row': row, 'slot': slot, 'entity_number': fields[0],
                                        'pointer_field_offset': 4 + row * 32 + slot * 4})
    return labels, count, list(strings.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    targets_path = ROOT / 'work/translation/en/character_labels.targets.json'
    targets = json.loads(targets_path.read_text(encoding='utf-8'))['translations'] if targets_path.exists() else {}
    with GameSource() as source:
        data, row_count, entries = collect(source)
        known_ids = {entry['id'] for entry in entries}
        if set(targets) - known_ids:
            raise ValueError('Target file refers to unknown character labels')
        for entry in entries:
            target = targets.get(entry['id'])
            if target and target['source_sha256'] != entry['source_sha256']:
                raise ValueError('Target source hash mismatch: ' + entry['id'])
        report = {'schema_version': 1, 'source_iso_sha256': source.manifest['source']['iso_sha256'],
                  'source_tables': ['01:00001/00000', '00:00044/00006/00000'],
                  'source_table_sha256': hashlib.sha256(data).hexdigest(),
                  'encoding': 'cp932', 'row_count': row_count, 'record_stride': 32,
                  'unique_string_count': len(entries), 'reference_count': sum(len(e['references']) for e in entries),
                  'japanese_string_count': sum(e['contains_japanese'] for e in entries),
                  'draft_target_count': len(targets), 'inserted_count': 0, 'visually_verified_count': 0,
                  'entries': entries}
        samples = []
        for entry in entries[:10]:
            p = entry['source_offset']
            text = data[p:p + entry['source_byte_length']].decode('cp932')
            samples.append({'id': entry['id'], 'source_ui_label': text,
                            'target': targets.get(entry['id'], {}).get('text'),
                            'references': len(entry['references'])})
    destination = ROOT / 'work/translation/en/character_labels.index.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'counts': {key: report[key] for key in ['row_count', 'unique_string_count', 'reference_count',
                                                            'japanese_string_count', 'draft_target_count']},
                      'samples': samples}, ensure_ascii=True, indent=2))
    if args.write:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
