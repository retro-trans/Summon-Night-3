"""Execute emitted pool hooks with checked allocation/lifetime contracts; preview first."""
import argparse
from datetime import datetime, timezone
import json
import struct

from dialogue_layout import verify_page_capacity, PIXEL_PAGE_CAPACITY
from font_patch import build_patch, FONT_POOL_CAPACITY, FONT_OBJECT_BYTES, sha
from sn3_archive import ROOT
from verify_font_patch import Machine


class PoolMachine(Machine):
    def __init__(self, patched, report, base):
        super().__init__(patched, report, base)
        self.blocks, self.events, self.serial, self.fail_allocation = {}, [], 0, False
        for address, method in [(0x1ea6cc, self.allocate), (0x1cba50, self.construct),
                                (0x68a2c, self.bind), (0x68b00, self.clear),
                                (0x1cba8c, self.destruct), (0x1ea718, self.free),
                                (0x68710, self.reset), (0x68ac4, self.close)]:
            self.native_handlers[base + address] = method

    def word(self, address, value):
        self.store(address, struct.pack('<I', value))

    def allocate(self, m):
        assert m.reg[4] == 192 * 224
        if self.fail_allocation:
            return {'v0': 0}
        address = 0x09000000 + self.serial * 0x10000
        self.serial += 1
        self.store(address - 16, bytes([0xa5]) * (192 * 224 + 32))
        self.blocks[address] = {'constructed': set(), 'cached': set()}
        self.events.append(('allocate', address))
        return {'v0': address}

    def object_at(self, address):
        candidates = [p for p in self.blocks if p <= address < p + 192 * 224]
        assert len(candidates) == 1
        p = candidates[0]
        assert (address - p) % 224 == 0
        return p, (address - p) // 224, self.blocks[p]

    def construct(self, m):
        p, index, block = self.object_at(m.reg[4])
        assert index not in block['constructed']
        block['constructed'].add(index)
        self.word(m.reg[4] + 0xb4, self.base + 0x22c4f0)
        self.word(m.reg[4] + 0xc0, 0)
        return {'v0': m.reg[4]}

    def bind(self, m):
        context, pointer, count = m.reg[4:7]
        assert count == 192 and self.blocks[pointer]['constructed'] == set(range(192))
        assert self.read(context + 0x30, 4) == 0
        self.word(context + 0x30, pointer)
        self.word(context + 0x34, count)
        self.events.append(('bind', context, pointer))
        return {}

    def clear(self, m):
        p, count = self.read(m.reg[4] + 0x30, 4), self.read(m.reg[4] + 0x34, 4)
        assert count == 192 and p in self.blocks
        self.blocks[p]['cached'].clear()
        self.events.append(('clear', p))
        return {}

    def destruct(self, m):
        p, index, block = self.object_at(m.reg[4])
        assert m.reg[5] == 0 and not block['cached']
        assert index in block['constructed']
        block['constructed'].remove(index)
        return {}

    def free(self, m):
        p = m.reg[4]
        assert p in self.blocks and not self.blocks[p]['constructed'] and not self.blocks[p]['cached']
        assert self.bytes(p - 16, 16) == bytes([0xa5]) * 16
        assert self.bytes(p + 192 * 224, 16) == bytes([0xa5]) * 16
        del self.blocks[p]
        self.events.append(('free', p))
        return {}

    def reset(self, m):
        assert self.read(m.reg[4] + 0x34, 4) != 192
        self.word(m.reg[4] + 0x30, 0)
        self.word(m.reg[4] + 0x34, 0)
        self.events.append(('reset', m.reg[4]))
        return {}

    def close(self, m):
        self.reset(m)
        self.events.append(('close', m.reg[4]))
        return {}


def verify():
    assert FONT_POOL_CAPACITY == PIXEL_PAGE_CAPACITY == 192 and FONT_OBJECT_BYTES == 224
    patched, report = build_patch()
    cases, allocated = 0, 0
    for base in (0x08804000, 0x0890c000):
        m = PoolMachine(patched, report, base)
        stack = 0x09f00000
        m.store(stack - 256, bytes(512))
        m.set('sp', stack)
        for n in range(16, 24):
            m.reg[n] = 0x12340000 + n
        saved = m.reg[16:24]
        contexts = [0x09e00000, 0x09e10000]
        for context in contexts:
            m.store(context, bytes(0x80))

        def run(hook, context):
            nonlocal cases
            m.set('a0', context)
            m.set('a1', 0x09d00000)
            m.set('a2', 64)
            m.run(report['labels'][hook])
            assert m.reg[29] == stack and m.reg[16:24] == saved
            cases += 1

        # Initial constructor reset and an old embedded pool must never free storage.
        run('pool_reset', contexts[0])
        m.word(contexts[0] + 0x30, 0x09d00000)
        m.word(contexts[0] + 0x34, 64)
        run('pool_close', contexts[0])
        assert not m.blocks and not any(e[0] == 'free' for e in m.events)
        # Two live contexts stay independent across page clear, reset, close, and reuse.
        for cycle in range(3):
            for context in contexts:
                run('pool_bind', context)
                p = m.read(context + 0x30, 4)
                for n in (64, 65, 69, 93, 192):
                    m.blocks[p]['cached'] = set(range(n))
                    m.set('a0', context)
                    m.clear(m)
                    assert len(m.blocks[p]['constructed']) == 192
                m.blocks[p]['cached'] = set(range(69))
            assert len(m.blocks) == 2
            run('pool_reset', contexts[0])
            assert len(m.blocks) == 1
            run('pool_close', contexts[1])
            assert not m.blocks
            run('pool_close', contexts[1])  # Idempotent; no double-free.
        allocated += m.serial
        m.fail_allocation = True
        try:
            run('pool_bind', contexts[0])
        except RuntimeError as exc:
            assert str(exc) == 'Emitted allocation failure trap'
            assert not m.blocks and m.read(contexts[0] + 0x30, 4) == 0
        else:
            raise AssertionError('Null allocation reached object construction')

    boundaries = []
    for count, cap, allowed in [(64, 64, True), (65, 64, False), (69, 64, False),
                                (65, 192, True), (69, 192, True), (93, 192, True),
                                (192, 192, True), (193, 192, False)]:
        try:
            verify_page_capacity(['i' * min(31, count - n) for n in range(0, count, 31)], cap)
            passed = True
        except ValueError:
            passed = False
        assert passed == allowed
        boundaries.append({'glyphs': count, 'capacity': cap, 'accepted': passed})
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'profile': report['profile'],
            'patched_elf_sha256': report['patched_elf_sha256'], 'hook_lifecycle_runs': cases,
            'separate_allocations_constructed_and_freed': allocated,
            'two_live_contexts_independent': True, 'null_allocation_trapped': True,
            'saved_registers_and_stack_preserved': True, 'boundary_cases': boundaries,
            'input_sha256': {p: sha((ROOT / p).read_bytes()) for p in
                             ['tools/font_patch.py', 'tools/verify_font_patch.py',
                              'tools/verify_font_pool.py', 'tools/dialogue_layout.py']},
            'scope_limit': 'Actual emitted MIPS with checked models of native allocation/constructor/cache/destructor contracts. Real heap, rendering, scene transitions and save/load still require runtime evidence.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = verify()
    destination = ROOT / 'docs/font_pool_validation_0.1.4.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'report': report}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
