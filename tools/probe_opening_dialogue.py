"""Inspect/advance a known opening candidate; preview actions and report writes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import struct
import time

from ppsspp_client import request, ROOT
from verify_runtime_scripts import memory


def observe(report, check_script=False):
    was_stepping = request('cpu.status')['stepping']
    if not was_stepping:
        request('cpu.stepping')
    try:
        vm = struct.unpack('<15I', memory(0x08a3a9e4, 60))
        if check_script:
            raw = memory(vm[7], report['decoded_size'])
            if hashlib.sha256(raw).hexdigest() != report['decoded_sha256']:
                raise ValueError('The running opening script does not match this candidate')
        state = memory(0x08e30910, 0x3d4)
        count, maximum = struct.unpack_from('<2I', state, 0x3cc)
        if count > 6:
            raise ValueError('Processed line count exceeds the known structure')
        physical = [r for r in report['changes'] if r['reference_instructions']]
        physical += [r for g in report.get('layout_groups', []) for page in g['pages'] for r in page]
        by_offset = {row['new_offset']: row for row in physical}
        rows = []
        for line in range(count):
            base = 0x84 + line * 0x8c
            pointer, choice_value = struct.unpack_from('<2I', state, base)
            cells, kinds = [], []
            for col in range(32):
                char, kind = struct.unpack_from('<2H', state, base + 10 + 4 * col)
                if not char:
                    break
                cells.append(struct.pack('<H', char))
                kinds.append(kind)
            raw = b''.join(cells)
            target = by_offset.get(pointer - vm[7])
            if target and raw != target['display_text'].encode('cp932'):
                raise ValueError('Processed characters differ from the translated string')
            rows.append({'id': target['id'] if target else None, 'target_text': target['text'] if target else None,
                         'source_pointer': hex(pointer), 'cell_count': len(cells),
                         'cell_sha256': hashlib.sha256(raw).hexdigest(), 'nonzero_kinds': sum(k != 0 for k in kinds),
                         'selectable': bool(state[base + 8]), 'choice_value': choice_value})
        return {'vm_pc_word': vm[1], 'native_call': hex(vm[12]), 'maximum_line_units': maximum,
                'lines': rows, 'choice_present': any(row['selectable'] for row in rows)}
    finally:
        if not was_stepping:
            request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.2')
    parser.add_argument('--advance-until', help='Stop when a displayed translated ID begins with this value')
    parser.add_argument('--max-presses', type=int, default=12)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--report-name', default='opening_progress')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version) or not re.fullmatch(r'[a-zA-Z0-9_-]+', args.report_name):
        raise ValueError('Invalid version or report name')
    if not 1 <= args.max_presses <= 40:
        raise ValueError('Press count must be 1..40')
    path = ROOT / 'work/output' / args.version / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    report = manifest['script_changes'][0]
    destination = path.parent / (args.report_name + '.json')
    if args.write and destination.exists():
        raise ValueError('Refusing to overwrite an existing trace')
    if request('game.status')['game']['id'] != 'NPJH50380':
        raise ValueError('Unexpected game')
    state = observe(report, check_script=True)
    states, presses, reason = [state], 0, 'inspection_only'
    print(json.dumps({'mode': 'execute' if args.execute else 'dry run', 'current': state,
                      'advance_until': args.advance_until, 'maximum_presses': args.max_presses,
                      'report_destination': str(destination) if args.write else None}), flush=True)
    if args.execute and args.advance_until:
        if request('cpu.status')['stepping']:
            request('cpu.resume')
        while presses < args.max_presses:
            if any((row['id'] or '').startswith(args.advance_until) for row in state['lines']):
                reason = 'target_reached'
                break
            if state['choice_present']:
                reason = 'stopped_before_choice_selection'
                break
            before = [r['source_pointer'] for r in state['lines']]
            request('input.buttons.press', button='circle', duration=2)
            presses += 1
            deadline = time.monotonic() + 4
            while time.monotonic() < deadline:
                time.sleep(0.25)
                state = observe(report)
                if state['lines'] and [r['source_pointer'] for r in state['lines']] != before:
                    time.sleep(1)
                    state = observe(report)
                    break
            if state != states[-1]:
                states.append(state)
                print(json.dumps({'press': presses, 'observed': state}), flush=True)
        else:
            reason = 'press_limit_reached'
        if any((row['id'] or '').startswith(args.advance_until) for row in state['lines']):
            reason = 'target_reached'
        observe(report, check_script=True)
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'version': args.version,
              'candidate_sha256': manifest['output_sha256'], 'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'complete_script_sha256_checked': report['decoded_sha256'], 'presses': presses,
              'result': reason, 'states': states,
              'scope_limit': 'Processed display cells and bounded input trace; screenshots and save/load are separate checks.'}
    print(json.dumps({'result': reason, 'presses': presses, 'observed_states': len(states), 'write': args.write}))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
