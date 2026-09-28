"""Index interface string references without retaining Japanese transcripts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

from sn3_archive import ROOT, GameSource, parse_index, child
from dialogue_encoding import control_tokens

JAPANESE = re.compile('[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]')
CATEGORIES = {
    0: 'status_labels', 1: 'stat_modifiers', 12: 'summon_names_and_forms',
    13: 'summon_abilities', 15: 'weapon_names', 16: 'armor_names',
    17: 'accessory_names', 19: 'items_and_descriptions', 20: 'ingredients',
    25: 'attack_commands', 28: 'special_commands', 31: 'skills',
    32: 'skill_short_descriptions', 34: 'shared_skills', 37: 'support_skills',
    38: 'help_and_menu_titles', 39: 'music_titles', 40: 'food_descriptions',
    45: 'common_brave_conditions', 46: 'battle_brave_conditions',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pool_rows(data, boundary):
    rows = []
    cursor = boundary
    while cursor < len(data):
        if data[cursor] == 0:
            cursor += 1
            continue
        end = data.find(b'\0', cursor)
        if end < 0:
            raise ValueError('Unterminated pool')
        raw = data[cursor:end]
        text = raw.decode('cp932', 'strict')
        if any(ord(character) < 32 for character in text):
            raise ValueError('Raw controls in candidate pool')
        rows.append({'source_offset': cursor, 'source_byte_length': len(raw),
                     'source_sha256': digest(raw), 'contains_japanese': bool(JAPANESE.search(text)),
                     'source_control_tokens': control_tokens(text)})
        cursor = end + 1
    return rows


def infer_table(data):
    count = struct.unpack_from('<I', data)[0]
    if not 0 < count < 10000:
        raise ValueError('Unbounded record count')
    candidates = []
    for dummy in (0, 1):
        records = count + dummy
        for stride in range(4, 1028, 4):
            boundary = 4 + records * stride
            if boundary >= len(data):
                break
            if data[boundary] == 0 or data[boundary - 1] != 0:
                continue
            try:
                rows = pool_rows(data, boundary)
            except (ValueError, UnicodeError):
                continue
            starts = {row['source_offset'] for row in rows}
            columns = []
            for slot in range(stride // 4):
                values = [struct.unpack_from('<I', data, 4 + row * stride + slot * 4)[0]
                          for row in range(records)]
                if any(value in starts for value in values) and all(value == 0 or value in starts for value in values):
                    columns.append(slot)
            if columns:
                candidates.append((records, stride, boundary, columns, rows))
    if len(candidates) != 1:
        raise ValueError('Expected one bounded table layout; got %d' % len(candidates))
    records, stride, boundary, columns, rows = candidates[0]
    by_offset = {row['source_offset']: row for row in rows}
    for row in rows:
        row['references'] = []
    for record in range(records):
        for slot in columns:
            field = 4 + record * stride + slot * 4
            value = struct.unpack_from('<I', data, field)[0]
            if value:
                by_offset[value]['references'].append({'record': record, 'slot': slot, 'pointer_field_offset': field})
    preceding = None
    for row in rows:
        if row['references']:
            row['ownership_status'] = 'direct_pointer'
            preceding = row['source_offset']
        else:
            row['ownership_status'] = 'pool_string_consumer_unverified'
            row['preceding_referenced_string_offset'] = preceding
            row['ownership_note'] = 'Pool adjacency is context only, not a proven runtime reference. May be a subsequent line of a multi-string field.'
    return {'header_count': count, 'record_count': records, 'record_stride': stride,
            'pool_offset': boundary, 'pointer_slots': columns, 'strings': rows}


def collect():
    tables, rejected = [], []
    with GameSource() as source:
        pack_data = source.resource('02.DAT', 3)
        pack = parse_index(pack_data, len(pack_data))
        resident = source.resource('00.DAT', 44)
        resident_pack = parse_index(resident, len(resident))
        if child(resident, resident_pack, 7) != pack_data:
            raise ValueError('Static UI table copies do not match')
        for number, category in CATEGORIES.items():
            data = child(pack_data, pack, number)
            try:
                table = infer_table(data)
            except ValueError as exc:
                rejected.append({'id': '02:00003/%05d' % number, 'category': category, 'reason': str(exc)})
                continue
            table.update({'id': '02:00003/%05d' % number, 'category': category,
                          'source_sha256': digest(data), 'resource_path': [3, number],
                          'duplicate_resource_ids': ['00:00044/00007/%05d' % number],
                          'category_status': 'source-sample classification; all records still require contextual review'})
            for row in table['strings']:
                row['id'] = table['id'] + ':ui:%08x' % row['source_offset']
                row['category'] = category
            tables.append(table)
        source_sha = source.manifest['source']['iso_sha256']
    elf = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    if digest(elf) != '82cc184377986d90d298ee4918fb11bd0e3524659e5c6f8b7b3c859f4d232684':
        raise ValueError('Unrecognized source executable')
    literals = []
    for match in re.finditer(rb'[^\x00]+', elf[0x214780:0x221e78]):
        raw = match.group()
        if len(raw) < 2 or len(raw) > 2048:
            continue
        try:
            text = raw.decode('cp932')
        except UnicodeError:
            continue
        if not re.search('[\u3040-\u30ff\u3400-\u9fff]', text) or any(ord(c) < 32 for c in text):
            continue
        offset = 0x214780 + match.start()
        literals.append({'id': 'elf:ui:%08x' % offset, 'source_offset': offset,
                         'module_address': hex(offset - 0xc0), 'source_byte_length': len(raw),
                         'source_sha256': digest(raw), 'source_control_tokens': control_tokens(text),
                         'category': 'executable_text_pending_consumer_classification'})
    rows = [row for table in tables for row in table['strings']]
    return {'schema_version': 1, 'source_iso_sha256': source_sha,
            'source_elf_sha256': digest(elf), 'status': 'interface discovery in progress; not full-game coverage',
            'scope': 'Validated shared static text tables and candidate Japanese executable literals. Source text is resolved locally, not exported.',
            'tables': tables, 'rejected_tables': rejected, 'executable_literals': literals,
            'statistics': {'validated_tables': len(tables), 'table_strings': len(rows),
                           'japanese_table_strings': sum(row['contains_japanese'] for row in rows),
                           'table_pointer_references': sum(len(row['references']) for row in rows),
                           'table_strings_with_direct_references': sum(bool(row['references']) for row in rows),
                           'table_strings_with_unverified_consumers': sum(not row['references'] for row in rows),
                           'executable_literal_candidates': len(literals)},
            'additional_sources': ['work/translation/en/character_labels.index.json',
                                   'work/ui/setup_assets_complete/index.json',
                                   'work/translation/en/script_strings.index.json'],
            'remaining_discovery': ['Classify executable literals by actual consumer',
                                    'Decode and classify additional battle/menu/tutorial graphics',
                                    'Identify UI/tutorial text supplied by scripts',
                                    'Verify category completeness through game navigation'],
            'reinsertion_ready': False}


def source_text(identity, index=None):
    index = index or json.loads((ROOT / 'work/translation/en/interface.index.json').read_text(encoding='utf-8'))
    if identity.startswith('elf:'):
        row = next(row for row in index['executable_literals'] if row['id'] == identity)
        data = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    else:
        table = next(table for table in index['tables'] if any(row['id'] == identity for row in table['strings']))
        row = next(row for row in table['strings'] if row['id'] == identity)
        with GameSource() as source:
            pack = source.resource('02.DAT', 3)
            data = child(pack, parse_index(pack, len(pack)), table['resource_path'][1])
        if digest(data) != table['source_sha256']:
            raise ValueError('Source table changed')
    raw = data[row['source_offset']:row['source_offset'] + row['source_byte_length']]
    if digest(raw) != row['source_sha256']:
        raise ValueError('Source string changed')
    return raw.decode('cp932')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--report', default='work/translation/en/interface.index.json')
    args = parser.parse_args()
    destination = (ROOT / args.report).resolve()
    if ROOT not in destination.parents or (args.write and destination.exists()):
        parser.error('Output must be a new file within the workspace')
    report = collect()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'statistics': report['statistics'], 'rejected': report['rejected_tables'],
                      'sample_tables': [{key: t[key] for key in ['id', 'category', 'record_count', 'record_stride', 'pool_offset', 'pointer_slots']} for t in report['tables']],
                      'sample_rows': report['tables'][0]['strings'][:2]}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
