"""Verify the loaded executable hooks and current Latin glyph geometry; preview first."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import re
import struct

from font_metrics import collect
from ppsspp_client import request, ROOT
from probe_opening_dialogue import observe
from verify_runtime_scripts import memory


def code_memory(address, size):
    return base64.b64decode(request('memory.read', address=address, size=size, replacements=False)['base64'])


def inspect(version):
    manifest_path = ROOT / 'work/output' / version / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    patch = manifest['executable_patch']
    elf = (manifest_path.parent / 'EBOOT.elf').read_bytes()
    if hashlib.sha256(elf).hexdigest() != patch['patched_elf_sha256']:
        raise ValueError('Saved executable differs from the build manifest')
    base = 0x08804000
    was_stepping = request('cpu.status')['stepping']
    if not was_stepping:
        request('cpu.stepping')
    try:
        offset = patch['added_segment_file_offset']
        expected = bytearray(elf[offset:offset + patch['added_segment_bytes']])
        for location, info in patch['extra_relocation_records']:
            word = struct.unpack_from('<I', expected, location)[0]
            kind = info & 15
            if kind == 4:
                word = (word & 0xfc000000) | (((word & 0x3ffffff) + (base >> 2)) & 0x3ffffff)
            elif kind == 5:
                low = struct.unpack_from('<h', expected, location + 4)[0]
                full = ((word & 65535) << 16) + low + base
                word = (word & 0xffff0000) | (((full + 0x8000) >> 16) & 65535)
            elif kind == 6:
                word = (word & 0xffff0000) | (((word & 65535) + base) & 65535)
            else:
                raise ValueError('Unknown added relocation')
            struct.pack_into('<I', expected, location, word)
        address = base + int(patch['added_segment_module_address'], 16)
        if code_memory(address, len(expected)) != expected:
            raise ValueError('Loaded added segment differs from the relocated executable')
        for hook in patch['hooks']:
            actual = struct.unpack('<I', code_memory(base + int(hook['module_address'], 16), 4))[0]
            target = base + int(hook['new_target'], 16)
            if actual != (3 << 26 | target >> 2):
                raise ValueError('Loaded hook jump differs')
        state = observe(manifest['script_changes'][0], check_script=True)
        if any(not row['id'] or row['nonzero_kinds'] for row in state['lines']):
            raise ValueError('Current page is not fully mapped token-free English')
        context = memory(0x08e30910, 0x4be4)
        count = struct.unpack_from('<I', context, 0x4be0)[0]
        pointer, capacity = struct.unpack_from('<2I', context, 0x30)
        expected_capacity = patch.get('font_pool', {}).get('capacity', 64)
        if capacity != expected_capacity or count > capacity:
            raise ValueError('Page exceeds or differs from the executable font-pool capacity')
        pool = memory(pointer, capacity * 0xe0)
        if any(struct.unpack_from('<I', pool, n * 0xe0 + 0xb4)[0] != base + 0x22c4f0
               for n in range(capacity)):
            raise ValueError('Font pool contains an unconstructed or wrong-type object')
        if patch.get('font_pool') and pointer < 0x08e30910 - 0x80 + 0x8af0 and pointer + len(pool) > 0x08e30910 - 0x80:
            raise ValueError('Expanded font pool overlaps the original parent object')
        if count != sum(row['cell_count'] for row in state['lines']):
            raise ValueError('Glyph count differs from processed cells')
        metrics = collect()[0]['characters']
        metrics_by_code = {int.from_bytes(bytes.fromhex(row['cp932_hex']), 'little'): row
                           for row in metrics.values()}
        number, evidence = 0, []
        for line_index, row in enumerate(state['lines']):
            pen = 0
            positions = []
            for char_index, char in enumerate(row['target_text']):
                source_code = struct.unpack_from('<H', context, 0x84 + line_index * 0x8c + 10 + char_index * 4)[0]
                if source_code not in metrics_by_code:
                    raise ValueError('Current processed character has no verified metric')
                metric = metrics_by_code[source_code]
                offset = 0x3e0 + number * 0x60
                width, height = struct.unpack_from('<2f', context, offset + 4)
                x = struct.unpack_from('<f', context, offset + 0x40)[0]
                anchor_x = struct.unpack_from('<f', context, offset + 0x50)[0]
                actual_line = struct.unpack_from('<I', context, offset + 0x58)[0]
                delta = 3 - metric['ink_bounds_inclusive'][0] if metric['ink_bounds_inclusive'] else 3
                expected_x = pen + 8 + delta
                if context[offset + 0xc] != 0 or (width, height) != (16.0, 16.0):
                    raise ValueError('Current glyph has an unsupported style or dimensions')
                if abs(x - expected_x) > 0.001 or abs(anchor_x - expected_x) > 0.001 or actual_line != line_index:
                    raise ValueError('Actual glyph position differs at line %d character %d: %s vs %s' %
                                     (line_index, len(positions), x, expected_x))
                if struct.unpack_from('<I', context, offset)[0] != pointer + number * 0xe0:
                    raise ValueError('Glyph does not reference its corresponding font object')
                positions.append(x)
                pen += metric['proposed_advance_pixels']
                number += 1
            evidence.append({'id': row['id'], 'text': row['target_text'], 'glyphs': len(positions),
                             'measured_width_pixels': pen + 2, 'actual_x_positions': positions})
        return {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'version': version,
                'candidate_sha256': manifest['output_sha256'],
                'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                'patched_elf_sha256': patch['patched_elf_sha256'], 'module_base': hex(base),
                'complete_added_segment_bytes_verified': len(expected), 'both_hook_jumps_verified': True,
                'hook_jumps_verified': len(patch['hooks']),
                'font_pool_pointer': hex(pointer), 'font_pool_capacity_verified': capacity,
                'font_objects_constructed_verified': capacity,
                'complete_script_sha256_verified': manifest['script_changes'][0]['decoded_sha256'],
                'glyph_geometry_checked': count, 'lines': evidence, 'state': state,
                'scope_limit': 'Loaded code and current page geometry. Screenshots, other pages/styles, choices, tokens and save/load are separate checks.'}
    finally:
        if not was_stepping:
            request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.4')
    parser.add_argument('--report-name', default='font_runtime_validation')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version) or not re.fullmatch(r'[a-zA-Z0-9_-]+', args.report_name):
        raise ValueError('Invalid version or report name')
    destination = ROOT / 'work/output' / args.version / (args.report_name + '.json')
    report = inspect(args.version)
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'report': report}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
