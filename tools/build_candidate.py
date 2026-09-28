"""Build and statically verify a versioned translation candidate; preview first."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
from character_labels import collect
from scan_source import inventory
from sn3_archive import GameSource, ROOT, parse_index, child
from sn3_repack import repack, relocate_labels, plan_bank, write_bank
from sn3_codec import compress, decompress
from script_repack import relocate_script
from script_strings import parse_pool
from dialogue_encoding import control_tokens
from dialogue_layout import PROFILE as LAYOUT_PROFILE, PIXEL_PROFILE, PIXEL_PAGE_CAPACITY, layout_dialogue, verify_layout
from font_patch import build_patch, PROFILE as FONT_PROFILE, FONT_POOL_CAPACITY


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def prepare(source):
    targets = json.loads((ROOT / 'work/translation/en/character_labels.targets.json').read_text())['translations']
    data, _, entries = collect(source)
    new_labels, changes = relocate_labels(data, entries, targets)
    bank_character = repack(source.resource('01.DAT', 1), {0: new_labels})
    plan01 = plan_bank(source, '01.DAT', {1: bank_character})
    master = source.resource('00.DAT', 44)
    master_index = parse_index(master, len(master))
    cached_character = repack(child(master, master_index, 6), {0: new_labels})
    new_master = repack(master, {0: plan01['index_bytes'], 6: cached_character})
    plan00 = plan_bank(source, '00.DAT', {44: new_master})
    return [plan00, plan01], changes, entries


def prepare_scripts(source, target_path, font_profile=None):
    """Prepare the opening-scene runtime pilot; other loader regions need mapping."""
    targets = json.loads(target_path.read_text(encoding='utf-8'))
    if targets.get('required_font_profile') and targets['required_font_profile'] != font_profile:
        raise ValueError('Pixel layout requires its matching executable font patch')
    index = json.loads((ROOT / 'work/translation/en/script_strings.index.json').read_text())
    if index['schema_version'] != 2 or targets['source_iso_sha256'] != index['source_iso_sha256']:
        raise ValueError('Script index/source identity mismatch')
    resource = next(r for r in index['resources'] if r['id'] == targets['resource_id'])
    if resource['id'] != '00:00065' or resource['path'] != [65]:
        raise ValueError('Only the mapped opening main-script region is enabled for this runtime pilot')
    raw = source.resource('00.DAT', 65)
    if hashlib.sha256(raw).hexdigest() != resource['sha256']:
        raise ValueError('Original script resource hash mismatch')
    key = int(resource['compression']['key'], 16)
    data = decompress(raw, key)[0]
    rows = {row['id']: row for row in resource['strings']}
    selected = {}
    for identity, target in targets['translations'].items():
        if identity not in rows or target.get('status') != 'meaning_reviewed':
            raise ValueError('Script target is unknown or lacks meaning review: ' + identity)
        if target.get('encoding_profile') != 'dialogue_fullwidth_cp932':
            raise ValueError('Opening dialogue pilot requires the two-byte display profile')
        selected[rows[identity]['source_offset']] = target
    if not selected:
        raise ValueError('Script target selection is empty')
    layouts = []
    if targets.get('layout_profile'):
        if targets['layout_profile'] not in (LAYOUT_PROFILE, PIXEL_PROFILE):
            raise ValueError('Unknown dialogue layout profile')
        for name, expected_hash in targets['review_inputs_sha256'].items():
            path = (ROOT / name).resolve()
            if ROOT not in path.parents or hash_file(path) != expected_hash:
                raise ValueError('Layout review input changed: ' + name)
        if targets['layout_profile'] == PIXEL_PROFILE and font_profile != FONT_PROFILE:
            raise ValueError('Pixel layout cannot be built with the original font renderer')
        if targets['layout_profile'] == PIXEL_PROFILE and not (
                targets.get('required_font_pool_capacity') == PIXEL_PAGE_CAPACITY == FONT_POOL_CAPACITY):
            raise ValueError('Pixel layout requires matching initialized font-object capacity')
        relocated, changes, layouts = layout_dialogue(data, selected, targets['layout_groups'], targets['layout_profile'])
    else:
        relocated, changes = relocate_script(data, selected)
    # Fixed loader start spacing, not a general production allocation policy.
    # The candidate must still pass live allocation and rendering checks.
    if len(relocated) > 0x78000:
        raise ValueError('Expanded main script needs a new runtime allocation before building')
    for change in changes:
        if control_tokens(change['display_text']):
            raise ValueError('Pilot with runtime tokens needs a measured expansion/layout profile')
        if not change.get('layout_group_id') and change['new_byte_length'] // 2 >= 32:
            raise ValueError('Pilot line needs wrapping or expanded rendering structures; do not truncate it')
        change['id'] = '%s:text:%08x' % (resource['id'], change['old_offset'])
    packed = compress(relocated, key)
    if decompress(packed, key)[0] != relocated:
        raise ValueError('Re-encoded script did not round-trip')
    report = {'resource_id': resource['id'], 'bank': '00.DAT', 'resource_number': 65,
              'compression_key': hex(key), 'original_decoded_size': len(data),
              'decoded_size': len(relocated), 'encoded_size': len(packed),
              'decoded_sha256': hashlib.sha256(relocated).hexdigest(),
              'changes': changes, 'runtime_allocation_verified': False,
              'runtime_profile': 'Opening main-script pilot; fixed next-start bound 0x78000; no whole-game allocation claim',
              'layout_profile': targets.get('layout_profile'), 'layout_groups': layouts}
    return {65: packed}, [report]


def directory_records(stream):
    stream.seek(16 * 2048)
    pvd = stream.read(2048)
    if pvd[:7] != b'\x01CD001\x01':
        raise ValueError('Unsupported volume descriptor')
    root = pvd[156:190]
    queue = [(struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0], '')]
    seen, records, directories = set(), [], []
    while queue:
        sector, size, parent = queue.pop()
        if sector in seen:
            continue
        seen.add(sector)
        directories.append((sector, size))
        stream.seek(sector * 2048)
        data = stream.read(size)
        position = 0
        while position < size:
            length = data[position]
            if not length:
                position = (position // 2048 + 1) * 2048
                continue
            raw = data[position:position + length]
            if len(raw) < 34:
                raise ValueError('Invalid directory record')
            record_offset = sector * 2048 + position
            position += length
            name = raw[33:33 + raw[32]]
            if name in (b'\0', b'\1'):
                continue
            path = parent + '/' + name.decode('ascii').split(';')[0]
            extent, length_bytes = struct.unpack_from('<I', raw, 2)[0], struct.unpack_from('<I', raw, 10)[0]
            if raw[25] & 0x80:
                raise ValueError('Multi-extent ISO files are unsupported')
            if raw[25] & 2:
                queue.append((extent, length_bytes, path))
            else:
                records.append({'path': path, 'record_offset': record_offset, 'sector': extent, 'size_bytes': length_bytes})
    return pvd, directories, records


def copy_range(source, output, offset, size):
    source.seek(offset)
    while size:
        chunk = source.read(min(size, 4 * 1024 * 1024))
        if not chunk:
            raise ValueError('Unexpected end of source ISO')
        output.write(chunk)
        size -= len(chunk)


def write_iso(source, plans, destination, file_replacements=None):
    original = ROOT / 'work/source/original.iso'
    replacements = []
    for plan in plans:
        file = source.files[plan['bank']]
        replacements.append(dict(plan, iso_start=file['sector'] * 2048,
                                 iso_end=file['sector'] * 2048 + file['size_bytes'],
                                 path='/PSP_GAME/USRDIR/' + plan['bank'], file_size=plan['new_size']))
    for path, payload in (file_replacements or {}).items():
        file = next(row for row in source.manifest['files'] if row['path'] == path)
        old_span = (file['size_bytes'] + 2047) // 2048 * 2048
        new_span = (len(payload) + 2047) // 2048 * 2048
        replacements.append({'path': path, 'payload': payload, 'file_size': len(payload),
                             'iso_start': file['sector'] * 2048, 'iso_end': file['sector'] * 2048 + old_span,
                             'old_size': old_span, 'new_size': new_span})
    replacements.sort(key=lambda row: row['iso_start'])
    if any(a['iso_end'] > b['iso_start'] for a, b in zip(replacements, replacements[1:])):
        raise ValueError('ISO replacement extents overlap')
    total_delta = sum(row['new_size'] - row['old_size'] for row in replacements)
    if total_delta % 2048:
        raise ValueError('Replacement growth must be sector-aligned')
    with original.open('rb') as input_iso:
        pvd, directories, records = directory_records(input_iso)
        first_change = replacements[0]['iso_start']
        if any(sector * 2048 + size > first_change for sector, size in directories):
            raise ValueError('Directory relocation is not implemented for this image layout')
        path_table_size = struct.unpack_from('<I', pvd, 132)[0]
        path_tables = struct.unpack_from('<II', pvd, 140) + struct.unpack_from('>II', pvd, 148)
        if any(sector * 2048 + path_table_size > first_change for sector in path_tables if sector):
            raise ValueError('Path-table relocation is not implemented for this image layout')
        input_iso.seek(17 * 2048)
        if input_iso.read(7) != b'\xffCD001\x01':
            raise ValueError('Additional volume descriptors require explicit support')
        original_size = original.stat().st_size
        if struct.unpack_from('<I', pvd, 80)[0] * 2048 != original_size:
            raise ValueError('Source volume size mismatch')
        with destination.open('xb') as output:
            cursor = 0
            for plan in replacements:
                copy_range(input_iso, output, cursor, plan['iso_start'] - cursor)
                if 'payload' in plan:
                    output.write(plan['payload'])
                    output.write(bytes(plan['new_size'] - len(plan['payload'])))
                else:
                    write_bank(source, plan, output)
                cursor = plan['iso_end']
            copy_range(input_iso, output, cursor, original_size - cursor)
    sizes = {row['path']: row['file_size'] for row in replacements}
    with destination.open('r+b') as output:
        for record in records:
            delta = sum(row['new_size'] - row['old_size'] for row in replacements
                        if row['iso_end'] <= record['sector'] * 2048)
            new_sector = record['sector'] + delta // 2048
            new_size = sizes.get(record['path'], record['size_bytes'])
            output.seek(record['record_offset'] + 2)
            output.write(struct.pack('<I', new_sector) + struct.pack('>I', new_sector))
            output.seek(record['record_offset'] + 10)
            output.write(struct.pack('<I', new_size) + struct.pack('>I', new_size))
        sectors = (original_size + total_delta) // 2048
        output.seek(16 * 2048 + 80)
        output.write(struct.pack('<I', sectors) + struct.pack('>I', sectors))
    if destination.stat().st_size != original_size + total_delta:
        raise ValueError('Output ISO size mismatch')


def extent_hash(stream, sector, length):
    stream.seek(sector * 2048)
    digest = hashlib.sha256()
    while length:
        block = stream.read(min(length, 4 * 1024 * 1024))
        if not block:
            raise ValueError('Short extent during verification')
        digest.update(block)
        length -= len(block)
    return digest.hexdigest()


def verify_candidate(path, original_source, changes, entries, script_changes=None, file_replacements=None, native_packs=None):
    script_changes = script_changes or []
    changed_banks = {'00.DAT': {44} | {r['resource_number'] for r in script_changes}, '01.DAT': {1}}
    for bank, packs in (native_packs or {}).items():
        changed_banks[bank] = set(packs)
    unchanged_files = []
    changed_files = []
    with path.open('rb') as candidate_iso, (ROOT / 'work/source/original.iso').open('rb') as original_iso:
        volume, actual_files = inventory(candidate_iso, path.stat().st_size)
        expected = {row['path']: row for row in original_source.manifest['files']}
        if set(expected) != {row['path'] for row in actual_files}:
            raise ValueError('ISO file list changed unexpectedly')
        for row in actual_files:
            before = expected[row['path']]
            actual_hash = extent_hash(candidate_iso, row['sector'], row['size_bytes'])
            if row['path'] in (file_replacements or {}):
                payload = file_replacements[row['path']]
                if row['size_bytes'] != len(payload) or actual_hash != hashlib.sha256(payload).hexdigest():
                    raise ValueError('Replacement file differs: ' + row['path'])
                changed_files.append(dict(row, sha256=actual_hash))
            elif row['path'] in {'/PSP_GAME/USRDIR/'+b for b in changed_banks}:
                changed_files.append(dict(row, sha256=actual_hash))
            else:
                if row['size_bytes'] != before['size_bytes'] or actual_hash != extent_hash(original_iso, before['sector'], before['size_bytes']):
                    raise ValueError('Unmodified ISO file changed: ' + row['path'])
                unchanged_files.append(row['path'])
    unchanged_resources = 0
    with GameSource(path) as candidate:
        for bank, packs in (native_packs or {}).items():
            for number, payload in packs.items():
                actual=candidate.resource(bank,number)
                if actual[:len(payload)] != payload or any(actual[len(payload):]):
                    raise ValueError('Native UI pack differs from validated rendering')
        for bank, except_ids in changed_banks.items():
            for old in original_source.indexes[bank]['entries']:
                if old['id'] in except_ids or not old['size']:
                    continue
                if original_source.resource(bank, old['id']) != candidate.resource(bank, old['id']):
                    raise ValueError('Untouched resource changed: %s:%d' % (bank, old['id']))
                unchanged_resources += 1
        original_labels, _, _ = collect(original_source)
        labels, _, _ = collect(candidate)
        changed_ids = {change['id']: change for change in changes}
        for entry in entries:
            expected_text = changed_ids[entry['id']]['text'] if entry['id'] in changed_ids else None
            for reference in entry['references']:
                pointer = struct.unpack_from('<I', labels, reference['pointer_field_offset'])[0]
                actual_text = labels[pointer:].split(b'\0', 1)[0]
                if expected_text is not None:
                    if pointer < len(original_labels) or actual_text.decode('cp932') != expected_text:
                        raise ValueError('Translated label was not correctly relocated')
                elif actual_text != original_labels[entry['source_offset']:].split(b'\0', 1)[0]:
                    raise ValueError('Untranslated label changed')
        master_before = original_source.resource('00.DAT', 44)
        master_after = candidate.resource('00.DAT', 44)
        old_index = parse_index(master_before, len(master_before))
        new_index = parse_index(master_after, len(master_after))
        for i in range(old_index['count']):
            allowed_master = (0, 1, 6) if native_packs else (0, 6)
            if i not in allowed_master and child(master_before, old_index, i) != child(master_after, new_index, i):
                raise ValueError('Untouched master child changed')
        for report in script_changes:
            data = decompress(candidate.resource(report['bank'], report['resource_number']),
                              int(report['compression_key'], 16))[0]
            if hashlib.sha256(data).hexdigest() != report['decoded_sha256']:
                raise ValueError('Built script differs from the verified relocation')
            parsed = parse_pool(data)
            rows = {row['source_offset']: row for row in parsed['strings']}
            for change in report['changes']:
                row = rows[change['new_offset']]
                if row['reference_instructions'] != change['reference_instructions']:
                    raise ValueError('Built script references differ from relocation')
                actual = data[row['source_offset']:row['source_offset'] + row['source_byte_length']].decode('cp932')
                if actual != change['display_text']:
                    raise ValueError('Built dialogue display text differs from the target')
            verify_layout(data, report['changes'], report.get('layout_groups', []))
    return {'iso_file_count': volume['file_count'], 'validated_bank_indexes': 23,
            'unchanged_iso_files': len(unchanged_files), 'unchanged_bank_resources': unchanged_resources,
            'all_character_references_checked': sum(len(e['references']) for e in entries),
            'relocated_labels': len(changes), 'resident_and_bank_labels_identical': True,
            'relocated_dialogue_strings': sum(len(r['changes']) for r in script_changes),
            'reflowed_dialogue_groups': sum(len(r.get('layout_groups', [])) for r in script_changes),
            'additional_dialogue_pages': sum(len(g['pages']) - 1 for r in script_changes for g in r.get('layout_groups', [])),
            'changed_files': changed_files, 'runtime_verified': False, 'visual_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.0')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--script-targets', type=Path)
    parser.add_argument('--font-patch', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version):
        raise ValueError('Build version must be 0.x.y')
    destination = ROOT / 'work/output' / args.version
    iso_path = destination / ('Summon_Night_3_EN_' + args.version + '.iso')
    with GameSource() as source:
        plans, changes, entries = prepare(source)
        file_replacements, font_report = {}, None
        executable_growth = 0
        if args.font_patch:
            executable, font_report = build_patch()
            file_replacements['/PSP_GAME/SYSDIR/EBOOT.BIN'] = executable
            old_size = next(r['size_bytes'] for r in source.manifest['files'] if r['path'] == '/PSP_GAME/SYSDIR/EBOOT.BIN')
            executable_growth = ((len(executable) + 2047) // 2048 - (old_size + 2047) // 2048) * 2048
        script_changes = []
        if args.script_targets:
            target_path = args.script_targets.resolve()
            if ROOT not in target_path.parents:
                raise ValueError('Script targets must be inside this workspace')
            replacements, script_changes = prepare_scripts(source, target_path, FONT_PROFILE if args.font_patch else None)
            combined = dict(plans[0]['replacements'])
            combined.update(replacements)
            plans[0] = plan_bank(source, '00.DAT', combined)
        summary = {'mode': 'write' if args.write else 'dry run', 'version': args.version,
                   'output': str(iso_path), 'scope': 'Partial technical candidate: labels and optional opening dialogue pilot',
                   'banks': [{k: p[k] for k in ('bank', 'old_size', 'new_size')} for p in plans],
                   'iso_growth_bytes': sum(p['new_size'] - p['old_size'] for p in plans) + executable_growth,
                   'executable_patch': font_report,
                   'changes': changes, 'script_changes': script_changes, 'build_directory_exists': destination.exists()}
        print(json.dumps(summary, indent=2), flush=True)
        if not args.write:
            return
        if destination.exists():
            raise ValueError('Refusing to overwrite an existing build directory')
        if hash_file(ROOT / 'work/source/original.iso') != source.manifest['source']['iso_sha256']:
            raise ValueError('Source ISO hash mismatch')
        destination.mkdir(parents=True)
        partial = iso_path.with_suffix('.iso.partial')
        write_iso(source, plans, partial, file_replacements)
        validation = verify_candidate(partial, source, changes, entries, script_changes, file_replacements)
        partial.rename(iso_path)
        manifest = {'schema_version': 1, 'version': args.version, 'kind': 'partial_technical_candidate',
                    'built_at_utc': datetime.now(timezone.utc).isoformat(),
                    'source_iso_sha256': source.manifest['source']['iso_sha256'],
                    'output_iso': iso_path.name, 'output_size_bytes': iso_path.stat().st_size,
                    'output_sha256': hash_file(iso_path), 'changes': changes,
                    'script_changes': script_changes, 'static_validation': validation,
                    'executable_patch': font_report,
                    'inputs_sha256': {name: hash_file(ROOT / name) for name in
                                     ['tools/build_candidate.py', 'tools/sn3_repack.py', 'tools/sn3_archive.py',
                                      'tools/character_labels.py', 'work/translation/en/character_labels.targets.json',
                                      'work/glossary/entities.json', 'tools/script_repack.py',
                                      'tools/script_strings.py', 'tools/sn3_codec.py', 'tools/sn3_vm.py',
                                      'tools/dialogue_encoding.py', 'tools/dialogue_layout.py',
                                      'tools/prepare_opening_layout.py']},
                    'known_limits': ['Only selected label/dialogue drafts are included.',
                                     'Most Japanese text remains untranslated.',
                                     'Runtime loading, memory allocation, fonts, and layout require verification.',
                                     'No gameplay, branch, save/load, or full translation acceptance is claimed.']}
        if args.script_targets:
            manifest['inputs_sha256'][str(target_path.relative_to(ROOT)).replace('\\', '/')] = hash_file(target_path)
        if args.font_patch:
            for name in ['tools/font_patch.py', 'tools/font_metrics.py', 'tools/verify_font_patch.py', 'tools/verify_font_pool.py']:
                manifest['inputs_sha256'][name] = hash_file(ROOT / name)
            (destination / 'EBOOT.elf').write_bytes(executable)
        (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'built': str(iso_path), 'sha256': manifest['output_sha256'], 'validation': validation}, indent=2))


if __name__ == '__main__':
    main()
