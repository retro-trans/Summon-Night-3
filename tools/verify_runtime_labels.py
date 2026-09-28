"""Verify loaded candidate label pointers against a versioned ISO; report preview first."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
from character_labels import collect
from ppsspp_client import request
from sn3_archive import GameSource, ROOT


def inspect(version):
    build = ROOT / 'work/output' / version
    manifest = json.loads((build / 'manifest.json').read_text())
    with GameSource(build / manifest['output_iso']) as source:
        expected, count, entries = collect(source)
    game = request('game.status')['game']
    if not game or game['id'] != 'NPJH50380':
        raise ValueError('Wrong game or emulator is not running')
    first = manifest['changes'][0]
    needle = first['text'].encode('cp932') + b'\0'
    status = request('cpu.status')
    if not status['stepping']:
        request('cpu.stepping')
    try:
        bases = set()
        previous = b''
        for address in range(0x08800000, 0x0a000000, 0x100000):
            data = previous + base64.b64decode(request('memory.read', address=address, size=0x100000)['base64'])
            start = address - len(previous)
            position = data.find(needle)
            while position >= 0:
                bases.add(start + position - first['new_offset'])
                position = data.find(needle, position + 1)
            previous = data[-len(needle):]
        verified = []
        for address in sorted(bases):
            if not 0x08800000 <= address <= 0x0a000000 - len(expected):
                continue
            raw = base64.b64decode(request('memory.read', address=address, size=len(expected))['base64'])
            normalized = bytearray(raw)
            fields = 0
            for entry in entries:
                for reference in entry['references']:
                    field = reference['pointer_field_offset']
                    actual_pointer = struct.unpack_from('<I', raw, field)[0]
                    relative = struct.unpack_from('<I', expected, field)[0]
                    if actual_pointer != address + relative:
                        break
                    struct.pack_into('<I', normalized, field, relative)
                    fields += 1
            if bytes(normalized) == expected:
                verified.append({'address': hex(address), 'record_count': count,
                                 'table_bytes': len(expected), 'absolute_pointers_checked': fields,
                                 'normalized_table_sha256': hashlib.sha256(normalized).hexdigest()})
        if not verified:
            raise ValueError('No fully matching runtime label table was found')
        return {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'version': version,
                'candidate_sha256': manifest['output_sha256'], 'emulator': request('version')['version'],
                'game': game, 'verified_tables': verified, 'relocated_drafts_loaded': len(manifest['changes']),
                'visual_label_verification': False,
                'scope_limit': 'One live scene: table allocation, contents and every absolute pointer. No whole-game or visual fit claim.'}
    finally:
        if not status['stepping']:
            request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.0')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if Path(args.version).name != args.version or not args.version.startswith('0.'):
        raise ValueError('Invalid version directory')
    report = inspect(args.version)
    destination = ROOT / 'work/output' / args.version / 'runtime_validation.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'report': report}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            output.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
