"""Trace actual pool calls during bounded opening input; preview before execute/write."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import struct
import time
import uuid

import ppsspp_client
from ppsspp_client import ROOT, websocket
import probe_opening_dialogue
import verify_runtime_scripts

BASE = 0x08804000
CODE = BASE + 0x32dbc0
CONTEXT = 0x08e30910
PROFILE = 'latin_ink_spacing_pool192_v2'


class Connection:
    # One connection keeps request/reply ordering under our control. Use actual
    # stops rather than relying on emulator log output being enabled.
    def __init__(self):
        self.socket = websocket.create_connection('ws://127.0.0.1:19380/debugger',
                                                   timeout=15, suppress_origin=True)
        self.journal = None
        self.events = []
        self.replies = {}

    def record(self, row):
        if self.journal:
            self.journal.write(json.dumps(row) + '\n')
            self.journal.flush()

    def receive(self, timeout):
        self.socket.settimeout(timeout)
        try:
            item = json.loads(self.socket.recv())
        except websocket.WebSocketTimeoutException:
            return None
        if item.get('ticket'):
            self.replies[item['ticket']] = item
        return item

    def send(self, event, **params):
        ticket = str(uuid.uuid4())
        self.socket.send(json.dumps(dict(params, event=event, ticket=ticket)))
        return ticket

    def wait_response(self, event, ticket):
        end = time.monotonic() + 15
        while time.monotonic() < end:
            item = self.replies.pop(ticket, None)
            if item is None:
                item = self.receive(min(0.25, max(0.01, end - time.monotonic())))
            if item and (item.get('ticket') == ticket or
                         (event in ('cpu.stepping', 'cpu.resume') and item.get('event') == event)):
                self.replies.pop(ticket, None)
                if item.get('event') == 'error':
                    raise RuntimeError(item)
                return item
        raise TimeoutError('Debugger response timed out: ' + event)

    def request(self, event, **params):
        return self.wait_response(event, self.send(event, **params))

    def drain(self, seconds):
        end = time.monotonic() + seconds
        wall_end = time.monotonic() + 60
        by_address = {point['address']: point for point in points()}
        while True:
            status = self.request('cpu.status')
            if status['stepping']:
                started = time.monotonic()
                point = by_address.get(status['pc'])
                if point is None:
                    self.record({'type': 'unexpected_stop', 'cpu': status})
                    raise ValueError('CPU stopped outside this trace')
                if time.monotonic() >= wall_end or len(self.events) >= 400:
                    raise ValueError('Bounded trace event/time limit reached')
                fields = {key: self.request('cpu.evaluate', expression=value)['uintValue']
                          for key, value in point['fields'].items()}
                row = {'type': 'pool_event', 'sequence': len(self.events),
                       'name': point['name'], 'fields': fields, 'ticks': status['ticks']}
                if point['name'] in ('constructed', 'bound', 'clear_return'):
                    data = self.memory(fields['pool'], 192 * 0xe0)
                    row['all_objects'] = {
                        'native_font_vtables': sum(struct.unpack_from('<I', data, n * 0xe0 + 0xb4)[0] == BASE + 0x22c4f0 for n in range(192)),
                        'nonzero_cache_pointers': sum(struct.unpack_from('<I', data, n * 0xe0 + 0xc0)[0] != 0 for n in range(192)),
                    }
                self.events.append(row)
                self.record(row)
                self.request('cpu.resume')
                end += time.monotonic() - started
                continue
            if time.monotonic() >= end:
                break
            self.receive(min(0.1, max(0.01, end - time.monotonic())))

    def memory(self, address, size):
        return base64.b64decode(self.request('memory.read', address=address,
                                            size=size, replacements=False)['base64'])

    def flush_breakpoint_cache(self):
        # In 1.20.4, BreakpointManager::Update stores only the LAST changed
        # address until Frame(). Adding a batch while paused can therefore leave
        # earlier compiled blocks without breakpoint checks. A temporary disabled
        # memory check requests a whole-JIT invalidation (Update(0)); remove it
        # before resuming. This changes debugger instrumentation, not game RAM.
        try:
            self.request('memory.breakpoint.add', address=CONTEXT, size=4,
                         enabled=False, log=False, read=True, write=False)
        finally:
            self.request('memory.breakpoint.remove', address=CONTEXT, size=4)


def points():
    out = []

    def add(offset, name, fields, condition='', native=False):
        out.append({'address': (BASE if native else CODE) + offset, 'name': name,
                    'fields': dict(fields, pc='pc'), 'condition': condition})

    context = dict(ctx='a0', pool='[a0+0x30]', cap='[a0+0x34]', caller='ra')
    add(0, 'first_glyph', dict(record='a0', text='a1', obj='a2'),
        'a0 == %s' % hex(CONTEXT + 0x3e0))
    add(592, 'reset', context)
    add(632, 'close', context)
    add(0x68b00, 'page_clear', dict(ctx='a0', pool='[a0+0x30]', cap='[a0+0x34]',
                                  glyphs='[a0+0x4be0]', caller='ra'),
        'a0 == %s' % hex(CONTEXT), native=True)
    add(0x1ea6cc, 'allocate_enter', dict(ctx='s0', size='a0'),
        'ra == %s' % hex(CODE + 336), native=True)
    add(336, 'allocate_return', dict(ctx='s0', pool='v0'))
    ends = '(s2 == 0 || s2 == 0xbf)'
    add(0x1cba50, 'constructor_enter', dict(ctx='s0', obj='a0', index='s2'),
        'ra == %s && %s' % (hex(CODE + 368), ends), native=True)
    add(368, 'constructor_return', dict(ctx='s0', obj='s1', index='s2', vtable='[s1+0xb4]', cache='[s1+0xc0]'), ends)
    add(388, 'constructed', dict(ctx='s0', pool='[sp+0x30]', count='s2'))
    add(408, 'bound', dict(ctx='s0', pool='[s0+0x30]', cap='[s0+0x34]', count='s2'))
    add(496, 'clear_enter', dict(ctx='s0', pool='s1', cap='[s0+0x34]', glyphs='[s0+0x4be0]'))
    add(504, 'clear_return', dict(ctx='s0', pool='s1', glyphs='[s0+0x4be0]',
                                first_cache='[s1+0xc0]', last_cache='[s1+0xa7e0]'))
    add(0x1cba8c, 'destructor_enter', dict(ctx='s0', obj='a0', flag='a1', index='s2'),
        'ra == %s && %s' % (hex(CODE + 524), ends), native=True)
    add(524, 'destructor_return', dict(ctx='s0', obj='s1', index='s2', cache='[s1+0xc0]'), ends)
    add(0x1ea718, 'free_enter', dict(ctx='s0', pool='a0', count='s2'),
        'ra == %s' % hex(CODE + 556), native=True)
    add(556, 'free_return', dict(ctx='s0', pool='[sp+0x30]', count='s2'))
    add(564, 'release_done', dict(ctx='s0', pool='[s0+0x30]', cap='[s0+0x34]'))
    return out


def preflight(connection, manifest, directory):
    patch = manifest['executable_patch']
    if patch['profile'] != PROFILE or patch['font_pool']['capacity'] != 192:
        raise ValueError('This tracer is specific to the verified 192-object hook profile')
    elf = (directory / 'EBOOT.elf').read_bytes()
    if hashlib.sha256(elf).hexdigest() != patch['patched_elf_sha256']:
        raise ValueError('Executable hash differs')
    start = patch['added_segment_file_offset']
    code = bytearray(elf[start:start + patch['added_segment_bytes']])
    for offset, info in patch['extra_relocation_records']:
        word = struct.unpack_from('<I', code, offset)[0]
        kind = info & 15
        if kind == 4:
            word = (word & 0xfc000000) | (((word & 0x3ffffff) + (BASE >> 2)) & 0x3ffffff)
        elif kind == 5:
            low = struct.unpack_from('<h', code, offset + 4)[0]
            value = ((word & 65535) << 16) + low + BASE
            word = (word & 0xffff0000) | (((value + 0x8000) >> 16) & 65535)
        elif kind == 6:
            word = (word & 0xffff0000) | (((word & 65535) + BASE) & 65535)
        else:
            raise ValueError('Unknown relocation')
        struct.pack_into('<I', code, offset, word)
    if connection.memory(CODE, len(code)) != code:
        raise ValueError('Live hook segment differs')
    for hook in patch['hooks']:
        address = BASE + int(hook['module_address'], 16)
        expected = 3 << 26 | (BASE + int(hook['new_target'], 16)) >> 2
        if struct.unpack('<I', connection.memory(address, 4))[0] != expected:
            raise ValueError('Live hook call differs')
    # These labels pin instruction offsets used above to the known emitted layout.
    expected_labels = dict(pool_bind=300, pool_release=436, pool_release_done=564,
                           pool_reset=592, pool_close=632, pool_allocation_failed=672)
    if any(patch['labels'][key] != value for key, value in expected_labels.items()):
        raise ValueError('Trace instruction layout changed')
    return {'loaded_code_bytes_verified': len(code), 'loaded_hooks_verified': len(patch['hooks'])}


def snapshot(connection, script):
    was_stepping = connection.request('cpu.status')['stepping']
    if not was_stepping:
        connection.request('cpu.stepping')
    try:
        state = probe_opening_dialogue.observe(script, check_script=True)
        pool, cap = struct.unpack('<2I', connection.memory(CONTEXT + 0x30, 8))
        evidence = {'state': state, 'pool': hex(pool), 'capacity': cap}
        if cap == 192:
            objects = connection.memory(pool, cap * 0xe0)
            evidence['native_font_vtables'] = sum(struct.unpack_from('<I', objects, i * 0xe0 + 0xb4)[0] == BASE + 0x22c4f0 for i in range(cap))
            evidence['cached_objects'] = sum(struct.unpack_from('<I', objects, i * 0xe0 + 0xc0)[0] != 0 for i in range(cap))
        return evidence
    finally:
        if not was_stepping:
            connection.request('cpu.resume')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.1.4')
    parser.add_argument('--presses', type=int, default=1)
    parser.add_argument('--interval', type=float, default=3)
    parser.add_argument('--button', choices=['circle', 'up', 'down'], default='circle')
    parser.add_argument('--allow-choice', action='store_true', help='Explicitly permit the chosen input on the currently inspected choice')
    parser.add_argument('--report-name', default='font_pool_trace_01')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version) or not re.fullmatch(r'[A-Za-z0-9_-]+', args.report_name):
        parser.error('Invalid version/report name')
    if not 1 <= args.presses <= 40 or not 1 <= args.interval <= 10:
        parser.error('Use 1..40 presses and 1..10 seconds between inputs')
    if args.execute != args.write:
        parser.error('Actual input requires both --execute and --write so partial evidence is retained')
    directory = ROOT / 'work/output' / args.version
    path = directory / 'manifest.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    destination = directory / (args.report_name + '.jsonl')
    if args.write and destination.exists():
        parser.error('Refusing existing evidence')
    connection = Connection()
    # These helpers must not open secondary sockets (which disable log capture).
    probe_opening_dialogue.request = connection.request
    verify_runtime_scripts.request = connection.request
    installed = []
    executed = False
    original_stepping = None
    try:
        version = connection.request('version')
        if version['version'] != 'v1.20.4':
            raise ValueError('Tracer API was checked against PPSSPP 1.20.4')
        if connection.request('game.status')['game']['id'] != 'NPJH50380':
            raise ValueError('Unexpected game')
        for event in ('cpu.breakpoint.list', 'memory.breakpoint.list'):
            if connection.request(event)['breakpoints']:
                raise ValueError('Existing breakpoints must be preserved; refusing to add trace points')
        original_stepping = connection.request('cpu.status')['stepping']
        if not original_stepping:
            connection.request('cpu.stepping')
        verified = preflight(connection, manifest, directory)
        initial = snapshot(connection, manifest['script_changes'][0])
        header = {'type': 'header', 'started_at_utc': datetime.now(timezone.utc).isoformat(),
                  'version': args.version, 'candidate_sha256': manifest['output_sha256'],
                  'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                  'tool_sha256': hashlib.sha256((ROOT / 'tools/trace_font_pool.py').read_bytes()).hexdigest(),
                  'initial': initial, 'verified': verified, 'points': points(),
                  'button': args.button, 'maximum_presses': args.presses,
                  'allow_choice': args.allow_choice, 'interval_seconds': args.interval,
                  'trace_method': 'Pausing breakpoints, register evaluation and bounded memory reads, followed by resume',
                  'batch_invalidation': 'Temporary disabled 4-byte read watch at the context requests a whole-JIT invalidation, then is removed before execution',
                  'scope': 'Actual native call entry/return events, loop endpoint counters and complete pool snapshots at construction/bind/cache clear. Heap internals, save/load and other paths are separate checks.'}
        print(json.dumps({'mode': 'execute' if args.execute else 'dry run', 'destination': str(destination), **header}, indent=2), flush=True)
        if not args.execute:
            return
        connection.journal = destination.open('x', encoding='utf-8')
        connection.record(header)
        executed = True
        for point in points():
            # Track ownership before dispatch in case the reply is lost.
            installed.append(point['address'])
            connection.request('cpu.breakpoint.add', address=point['address'], enabled=True,
                               log=False, condition=point['condition'])
        active = connection.request('cpu.breakpoint.list')['breakpoints']
        if {p['address'] for p in active if p['enabled']} != set(installed):
            raise ValueError('Trace breakpoints did not become enabled')
        connection.record({'type': 'installed', 'breakpoints': active})
        connection.flush_breakpoint_cache()
        # PPSSPP applies pending JIT invalidations at frame boundaries. Let it
        # reach a frame boundary before the first input can change the page.
        connection.request('cpu.resume')
        connection.drain(0.25)
        connection.request('cpu.stepping')
        reason, presses = 'press_limit_reached', 0
        for _ in range(args.presses):
            current = snapshot(connection, manifest['script_changes'][0])
            if current['state']['choice_present'] and not args.allow_choice:
                reason = 'stopped_before_choice'
                break
            connection.request('cpu.resume')
            # Button completion is acknowledged on an emulated frame. Service
            # breakpoint stops meanwhile, or the acknowledgment can deadlock.
            input_ticket = connection.send('input.buttons.press', button=args.button, duration=2)
            presses += 1
            connection.drain(args.interval)
            connection.wait_response('input.buttons.press', input_ticket)
            status = connection.request('cpu.status')
            if status['stepping']:
                reason = 'unexpected_cpu_stop'
                connection.record({'type': 'unexpected_stop', 'cpu': status})
                break
            connection.request('cpu.stepping')
            state = snapshot(connection, manifest['script_changes'][0])
            connection.record({'type': 'after_input', 'button': args.button, 'press': presses, **state})
            print(json.dumps({'press': presses, 'pool_events': len(connection.events),
                              'choice': state['state']['choice_present'], 'pool': state['pool']}), flush=True)
            if len(connection.events) >= 400:
                reason = 'trace_event_limit'
                break
        connection.record({'type': 'result', 'reason': reason, 'presses': presses,
                           'events': dict(Counter(e['name'] for e in connection.events))})
    except Exception as error:
        connection.record({'type': 'error', 'error_type': type(error).__name__, 'message': str(error)})
        raise
    finally:
        cleanup_errors = []
        try:
            if executed and not connection.request('cpu.status')['stepping']:
                connection.request('cpu.stepping')
            for address in installed:
                try:
                    connection.request('cpu.breakpoint.remove', address=address)
                except Exception as error:
                    cleanup_errors.append(str(error))
            if installed:
                connection.flush_breakpoint_cache()
                remaining = connection.request('cpu.breakpoint.list')['breakpoints']
                if remaining:
                    cleanup_errors.append('Breakpoints remain: ' + str(remaining))
                if connection.request('memory.breakpoint.list')['breakpoints']:
                    cleanup_errors.append('Memory breakpoints remain')
            connection.record({'type': 'cleanup', 'errors': cleanup_errors,
                               'cpu_left_held': executed, 'trace_points_removed': len(installed) if not cleanup_errors else None})
            if not executed and original_stepping is False:
                connection.request('cpu.resume')
        finally:
            if connection.journal:
                connection.journal.close()
            connection.socket.close()
        if cleanup_errors:
            raise RuntimeError('Trace cleanup incomplete: ' + str(cleanup_errors))


if __name__ == '__main__':
    main()
