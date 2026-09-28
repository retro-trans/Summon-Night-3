"""Execute the emitted spacing hooks against their caller contracts; preview first."""
import argparse
from datetime import datetime, timezone
import json
import struct

from font_metrics import collect
from font_patch import build_patch, CODE_VA, REG, sha
from sn3_archive import ROOT


def signed(value, bits=32):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


class Machine:
    """Independent bounded executor for the actual emitted standard MIPS instructions.

    Only the two unmodified original callees are modeled, at their ABI boundaries.
    This does not model PSP rendering or replace clean-boot runtime validation.
    """
    def __init__(self, patched, report, base):
        self.mem, self.reg, self.fp = {}, [0] * 32, [0] * 32
        self.native_handlers = {}
        self.base, self.original_calls = base, []
        off, size = report['added_segment_file_offset'], report['added_segment_bytes']
        self.store(base + CODE_VA, patched[off:off + size])
        for offset, info in report['extra_relocation_records']:
            address = base + CODE_VA + offset
            word = self.read(address, 4)
            if info & 15 == 4:
                word = word & 0xfc000000 | ((word & 0x3ffffff) + (base >> 2)) & 0x3ffffff
            elif info & 15 == 5:
                low = signed(self.read(address + 4, 4) & 65535, 16)
                full = ((word & 65535) << 16) + low + base
                word = word & 0xffff0000 | ((full + 0x8000) >> 16) & 65535
            elif info & 15 == 6:
                word = word & 0xffff0000 | ((word & 65535) + base) & 65535
            else:
                raise AssertionError('Unexpected new relocation type')
            self.store(address, struct.pack('<I', word))

    def store(self, address, data):
        self.mem.update((address + i, b) for i, b in enumerate(data))

    def read(self, address, size):
        return int.from_bytes(bytes(self.mem[address + i] for i in range(size)), 'little')

    def bytes(self, address, size):
        return bytes(self.mem[address + i] for i in range(size))

    def set(self, name, value):
        self.reg[REG[name]] = value & 0xffffffff

    def float_store(self, address, value):
        self.store(address, struct.pack('<f', value))

    def float_read(self, address):
        return struct.unpack('<f', self.bytes(address, 4))[0]

    def run(self, entry):
        pc, stop = self.base + CODE_VA + entry, 0x0bad0000
        self.set('ra', stop)
        for step in range(20000):
            if pc == stop:
                return step
            if pc in self.native_handlers or pc in (self.base + 0x682e8, self.base + 0x685cc):
                self.original_calls.append((pc, tuple(self.reg[4:7])))
                returns = self.native_handlers[pc](self) if pc in self.native_handlers else {}
                if pc == self.base + 0x685cc:
                    scale = 1.2 if self.reg[5] in (1, 2, 3) else 1.0
                    self.float_store(self.reg[4], scale)
                    self.float_store(self.reg[4] + 4, scale)
                pc = self.reg[31]
                # Volatile registers may be clobbered by the original callee.
                for r in list(range(2, 16)) + [24, 25]:
                    self.reg[r] = 0xcafe0000 + r
                for name, value in returns.items():
                    self.set(name, value)
                continue
            word = self.read(pc, 4)
            op, rs, rt, rd = word >> 26, word >> 21 & 31, word >> 16 & 31, word >> 11 & 31
            immediate, next_pc, branch = signed(word & 65535, 16), pc + 4, False
            if word == 0:
                pass
            elif op == 0 and word & 63 == 0x21:
                self.reg[rd] = (self.reg[rs] + self.reg[rt]) & 0xffffffff
            elif op == 0 and word & 63 == 8:
                next_pc, branch = self.reg[rs], True
            elif op in (2, 3):
                if op == 3:
                    self.reg[31] = pc + 8
                next_pc, branch = (pc + 4) & 0xf0000000 | (word & 0x3ffffff) << 2, True
            elif op in (4, 5):
                condition = (self.reg[rs] == self.reg[rt]) == (op == 4)
                next_pc, branch = pc + 4 + immediate * 4 if condition else pc + 8, True
            elif op == 9:
                self.reg[rt] = (self.reg[rs] + immediate) & 0xffffffff
            elif op == 11:
                self.reg[rt] = int(self.reg[rs] < (immediate & 0xffffffff))
            elif op == 13:
                self.reg[rt] = self.reg[rs] | (word & 65535)
            elif word == 0x0d:
                raise RuntimeError('Emitted allocation failure trap')
            elif op == 15:
                self.reg[rt] = (word & 65535) << 16
            elif op in (32, 35, 36, 37):
                size = {32: 1, 35: 4, 36: 1, 37: 2}[op]
                value = self.read(self.reg[rs] + immediate, size)
                self.reg[rt] = (signed(value, 8) if op == 32 else value) & 0xffffffff
            elif op == 43:
                self.store(self.reg[rs] + immediate, struct.pack('<I', self.reg[rt]))
            elif op == 49:
                self.fp[rt] = self.read(self.reg[rs] + immediate, 4)
            elif op == 57:
                self.store(self.reg[rs] + immediate, struct.pack('<I', self.fp[rt]))
            elif op == 17:
                fs, fd, fn = rd, word >> 6 & 31, word & 63
                if rs == 4:
                    self.fp[fs] = self.reg[rt]
                elif rs == 20 and fn == 32:
                    self.fp[fd] = int.from_bytes(struct.pack('<f', signed(self.fp[fs])), 'little')
                elif rs == 16 and fn == 0:
                    x, y = (struct.unpack('<f', struct.pack('<I', self.fp[f]))[0] for f in (fs, rt))
                    self.fp[fd] = int.from_bytes(struct.pack('<f', x + y), 'little')
                else:
                    raise AssertionError('Unexpected FP instruction')
            else:
                raise AssertionError('Unexpected instruction %08x at %08x' % (word, pc))
            if branch:
                assert self.read(pc + 4, 4) == 0, 'Executor requires explicitly emitted nop delay slots'
            self.reg[0] = 0
            pc = next_pc
        raise AssertionError('Hook did not return within its instruction budget')


def verify():
    patched, report = build_patch()
    metrics, _ = collect()
    cases, max_steps = 0, 0
    # Both load bases exercise rebasing, including HI16 carry and signed LO16.
    for base in (0x08804000, 0x0890c000):
        for char, metric in list(metrics['characters'].items()) + [('unmapped', None)]:
            code = int.from_bytes(bytes.fromhex(metric['cp932_hex']), 'little') if metric else 0x4083
            for hook, last, style in [('glyph', False, 0), ('measure', False, 0), ('measure', True, 0),
                                      ('glyph', False, 2), ('measure', True, 2)]:
                m = Machine(patched, report, base)
                stack, cell, output = 0x09f00000, 0x09f01000, 0x09f02000
                m.store(stack - 64, bytes(320))
                m.store(cell, struct.pack('<HH', code, 0))
                m.store(output, bytes(8))
                m.set('sp', stack)
                for r in range(16, 24):
                    m.reg[r] = 0x12340000 + r
                m.set('s0', style)
                m.set('s1', 5)
                m.set('s2', cell)
                m.set('s4', 5 if last else 7)
                saved = m.reg[16:24]
                if hook == 'glyph':
                    m.set('a0', 0x09e00000)
                    m.set('a1', cell)
                    m.set('a2', 0x09e01000)
                    m.float_store(stack + 0x48, 16.0)
                    m.float_store(stack + 0x50, 72.0)
                    m.float_store(stack + 0x58, 72.0)
                    before = m.bytes(stack, 200)
                else:
                    m.set('a0', output)
                    m.set('a1', style)
                max_steps = max(max_steps, m.run(report['labels'][hook]))
                assert m.reg[29] == stack and m.reg[16:24] == saved
                assert len(m.original_calls) == 1
                if hook == 'glyph':
                    assert m.original_calls[0][1] == (0x09e00000, cell, 0x09e01000)
                    advance = metric['proposed_advance_pixels'] if metric and style == 0 else 16
                    delta = (3 - metric['ink_bounds_inclusive'][0] if metric['ink_bounds_inclusive'] else 3) if metric and style == 0 else 0
                    assert m.float_read(stack + 0x48) == advance
                    assert m.float_read(stack + 0x50) == 72 + delta
                    assert m.float_read(stack + 0x58) == 72 + delta
                    changed = set(range(0x48, 0x4c)) | set(range(0x50, 0x54)) | set(range(0x58, 0x5c))
                    after = m.bytes(stack, 200)
                    assert all(before[i] == after[i] for i in range(200) if i not in changed)
                else:
                    expected = metric['proposed_advance_pixels'] - 16 + (2 if last else 0) if metric and style == 0 else (1.2 if style else 1)
                    assert abs(m.float_read(output) - expected) < 0.00001
                    assert abs(m.float_read(output + 4) - (1.2 if style else 1)) < 0.00001
                cases += 1
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'profile': report['profile'], 'patched_elf_sha256': report['patched_elf_sha256'],
            'hook_cases': cases, 'load_bases': ['0x08804000', '0x0890c000'],
            'maximum_emitted_instructions_per_case': max_steps,
            'all_characters_default_and_nondefault_styles_checked': True,
            'unmapped_character_fallback_checked': True, 'callee_arguments_preserved': True,
            'saved_registers_and_stack_preserved': True, 'only_declared_caller_fields_changed': True,
            'last_cell_measurement_inset_checked': True,
            'input_sha256': {name: sha((ROOT / name).read_bytes()) for name in
                             ['tools/font_patch.py', 'tools/font_metrics.py', 'tools/verify_font_patch.py']},
            'scope_limit': 'Actual emitted hooks executed with modeled original callee contracts. PSP loader, rasterization, layout and hardware still require runtime checks.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--report', default='docs/font_patch_validation_0.1.4.json')
    args = parser.parse_args()
    report = verify()
    destination = (ROOT / args.report).resolve()
    if ROOT not in destination.parents:
        raise ValueError('Report must stay in workspace')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'report': report}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
