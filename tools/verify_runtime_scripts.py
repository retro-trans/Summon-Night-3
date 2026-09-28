"""Compare a pilot script and its processed display line with live game memory."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import re
import struct
from ppsspp_client import request, ROOT
from script_strings import parse_pool
from dialogue_layout import verify_layout


def memory(address, size):
    if not 0x08800000 <= address < address + size <= 0x0a000000:
        raise ValueError('Read is outside PSP user memory')
    return base64.b64decode(request('memory.read', address=address, size=size)['base64'])


def inspect(version, vm_address, text_context):
    manifest_path = ROOT / 'work/output' / version / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    reports = manifest.get('script_changes', [])
    if len(reports) != 1 or reports[0]['resource_id'] != '00:00065':
        raise ValueError('This verifier requires the opening main-script pilot')
    expected = reports[0]
    game = request('game.status')['game']
    if game['id'] != 'NPJH50380':
        raise ValueError('Unexpected running game')
    was_stepping = request('cpu.status')['stepping']
    if not was_stepping:
        request('cpu.stepping')
    try:
        fields = struct.unpack('<15I', memory(vm_address, 60))
        data = memory(fields[7], expected['decoded_size'])
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected['decoded_sha256']:
            raise ValueError('Complete live script differs from this candidate')
        parsed = parse_pool(data)
        verify_layout(data, expected['changes'], expected.get('layout_groups', []))
        by_offset = {row['source_offset']: row for row in parsed['strings']}
        for change in expected['changes']:
            row = by_offset[change['new_offset']]
            if row['reference_instructions'] != change['reference_instructions']:
                raise ValueError('Live script references differ')
            end = change['new_offset'] + change['new_byte_length']
            if data[end:end + 2] != b'\0\0':
                raise ValueError('Dialogue lacks a complete two-byte terminator')
        state = memory(text_context, 0x3d4)
        count, visible_count = struct.unpack_from('<2I', state, 0x3cc)
        if not 1 <= count <= 6:
            raise ValueError('Expected one or more processed display lines')
        displayed_ids = []
        cell_counts = []
        physical_records = [row for row in expected['changes'] if row['reference_instructions']]
        physical_records += [row for group in expected.get('layout_groups', []) for page in group['pages'] for row in page]
        for line in range(count):
            cells = []
            for column in range(32):
                character, kind = struct.unpack_from('<2H', state, 0x84 + line * 0x8c + 10 + column * 4)
                if character == 0:
                    break
                if kind != 0:
                    raise ValueError('This pilot verifier does not claim runtime-token coverage')
                cells.append(character)
            display = b''.join(struct.pack('<H', character) for character in cells).decode('cp932')
            pointer = struct.unpack_from('<I', state, 0x84 + line * 0x8c)[0]
            matches = [row['id'] for row in physical_records
                       if row['new_offset'] == pointer - fields[7] and row['display_text'] == display]
            if len(matches) != 1:
                raise ValueError('Current processed line is not a unique translated pilot line')
            displayed_ids.extend(matches)
            cell_counts.append(len(cells))
        return {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'version': version,
                'candidate_sha256': manifest['output_sha256'],
                'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                'emulator': request('version')['version'], 'source_disc_id': game['id'],
                'script_vm_address': hex(vm_address), 'script_base': hex(fields[7]),
                'bytes_checked': len(data), 'decoded_sha256': digest,
                'full_decoded_script_matches': True, 'relocated_strings_loaded': len(expected['changes']),
                'all_script_references_valid': True, 'two_byte_terminators_verified': True,
                'display_context': hex(text_context), 'processed_line_count': count,
                'processed_translated_ids': displayed_ids, 'processed_cell_counts': cell_counts,
                'visible_count_field': visible_count, 'native_call': hex(fields[12]),
                'scope_limit': 'One opening scene and one currently processed display. Does not prove every translated page, all fonts, expanded allocation across the game, branches, or save/load.'}
    finally:
        if not was_stepping:
            request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.1')
    parser.add_argument('--vm-address', type=lambda value: int(value, 0), default=0x08a3a9e4)
    parser.add_argument('--text-context', type=lambda value: int(value, 0), default=0x08e30910)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version):
        raise ValueError('Version must be 0.x.y')
    destination = ROOT / 'work/output' / args.version / 'script_runtime_validation.json'
    result = inspect(args.version, args.vm_address, args.text_context)
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'report': result}, indent=2))
    if args.write:
        if destination.exists():
            raise ValueError('Refusing to overwrite existing runtime evidence')
        destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
