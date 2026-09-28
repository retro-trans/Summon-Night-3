"""Preserve the known 0.1.3 opening fault without changing debugger or game state."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import struct

from ppsspp_client import request, ROOT
from probe_opening_dialogue import observe


def read(address, size):
    if not 0x08800000 <= address < address + size <= 0x0a000000:
        raise ValueError('Read outside PSP user memory')
    return base64.b64decode(request('memory.read', address=address, size=size,
                                    replacements=False)['base64'])


def inspect():
    path = ROOT / 'work/output/0.1.3/manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    before = request('cpu.status')
    if not before['stepping'] or before['pc'] != 0x1fb:
        raise ValueError('Requires the already-held, known 0.1.3 fault; no CPU action taken')
    if request('game.status')['game']['id'] != 'NPJH50380':
        raise ValueError('Unexpected game')
    category = request('cpu.getAllRegs')['categories'][0]
    regs = dict(zip(category['registerNames'], category['uintValues']))
    context = 0x08e30910
    header = read(context, 64)
    pool, capacity = struct.unpack_from('<2I', header, 0x30)
    if (pool, capacity, regs['s7'], regs['s0'], regs['ra']) != (
            0x08e35b70, 64, 64, 0x08e39370, 0x0886c328):
        raise ValueError('Fault does not match the measured context and call site')
    state = observe(manifest['script_changes'][0], check_script=True)
    if sum(row['cell_count'] for row in state['lines']) != 69:
        raise ValueError('Unexpected processed page')
    objects = read(pool, 65 * 0xe0)
    tables = [struct.unpack_from('<I', objects, i * 0xe0 + 0xb4)[0] for i in range(65)]
    if tables[:64] != [0x08a304f0] * 64 or tables[64] != 0:
        raise ValueError('Unexpected font-object table layout')
    original = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    if hashlib.sha256(original).hexdigest() != manifest['executable_patch']['source_elf_sha256']:
        raise ValueError('Original executable hash differs')
    instructions = {hex(va): hex(struct.unpack_from('<I', original, va + 0xc0)[0])
                    for va in (0x68320, 0x6b4bc, 0x6b50c, 0x6b510)}
    after = request('cpu.status')
    if (before['pc'], before['ticks'], before['stepping']) != (after['pc'], after['ticks'], after['stepping']):
        raise ValueError('CPU state changed while inspecting')
    return {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_version': '0.1.3', 'acceptance': 'failed_runtime_qa',
        'candidate_sha256_from_manifest': manifest['output_sha256'],
        'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_elf_sha256_verified': manifest['executable_patch']['source_elf_sha256'],
        'complete_live_script_sha256_verified': manifest['script_changes'][0]['decoded_sha256'],
        'cpu': {k: before[k] for k in ('pc', 'ticks', 'stepping', 'paused')},
        'registers_hex': {k: hex(v) for k, v in regs.items()},
        'text_context': hex(context), 'context_header_hex': header.hex(),
        'font_pool': hex(pool), 'font_object_stride_bytes': 0xe0,
        'font_pool_capacity': capacity, 'construction_index_zero_based': regs['s7'],
        'valid_object_vtables': {'count': 64, 'value': hex(tables[0])},
        'next_object': {'address': hex(pool + capacity * 0xe0), 'vtable': hex(tables[64]),
                        'bytes_hex': objects[64 * 0xe0:].hex()},
        'original_instruction_words': instructions, 'processed_page': state,
        'diagnosis': 'The 69-cell page attempts to construct object index 64 beyond the 64-object font pool. The original glyph initializer calls through an invalid virtual-method descriptor.',
        'cpu_state_unchanged': True,
        'scope_limit': 'One held fault. No input, resume, breakpoint, RAM write, screenshot capture, or repair. Allocation expansion and lifetime safety remain unverified.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    destination = ROOT / 'work/output/0.1.3/font_pool_fault.json'
    if args.write and destination.exists():
        raise ValueError('Refusing to overwrite fault evidence')
    report = inspect()
    print(json.dumps({'mode': 'write' if args.write else 'dry run',
                      'destination': str(destination), 'report': report}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
