"""Add relocatable Latin-spacing hooks to the verified PSP executable."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from font_metrics import collect, ELF_SHA256
from sn3_archive import ROOT

PROFILE = 'latin_ink_spacing_pool192_v2'
FONT_POOL_CAPACITY = 192
FONT_OBJECT_BYTES = 0xe0
CODE_VA = 0x32dbc0
HOOKS = {0x6a4a0: (0x682e8, 'glyph'), 0x6aa38: (0x685cc, 'measure'),
         0x6b50c: (0x68a2c, 'pool_bind'),
         0x6b304: (0x68710, 'pool_reset'), 0x6b4fc: (0x68710, 'pool_reset'),
         0x6b554: (0x68ac4, 'pool_close')}
REG = dict(zip(('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 '
                's0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra').split(), range(32)))


def align(n, boundary=64):
    return (n + boundary - 1) // boundary * boundary


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Assembler:
    """Small explicit MIPS-I/FP emitter; every absolute operand gets a PRX relocation."""
    def __init__(self):
        self.words, self.labels, self.fixups, self.relocs = [], {}, [], []

    def label(self, name):
        if name in self.labels:
            raise ValueError('Duplicate assembly label')
        self.labels[name] = len(self.words) * 4

    def emit(self, word):
        self.words.append(word)

    def i(self, opcode, rt, rs, immediate):
        if not -32768 <= immediate <= 65535:
            raise ValueError('Immediate does not fit')
        self.emit(opcode << 26 | REG[rs] << 21 | REG[rt] << 16 | (immediate & 65535))

    def move(self, rd, rs):
        self.emit(REG[rs] << 21 | REG[rd] << 11 | 0x21)

    def branch(self, opcode, rs, rt, label):
        self.fixups.append((len(self.words), 'branch', label))
        self.i(opcode, rt, rs, 0)
        self.emit(0)

    def jump(self, target, link=True):
        self.fixups.append((len(self.words), 'jump', target))
        self.relocs.append((len(self.words) * 4, 0x304))  # segment 3 location, segment 0 base, R_MIPS_26
        self.emit((3 if link else 2) << 26)
        self.emit(0)

    def table_address(self, rt):
        self.fixups.append((len(self.words), 'hi', 'table'))
        self.relocs.append((len(self.words) * 4, 0x305))
        self.i(15, rt, 'zero', 0)
        self.fixups.append((len(self.words), 'lo', 'table'))
        self.relocs.append((len(self.words) * 4, 0x306))
        self.i(9, rt, rt, 0)

    def fp_mem(self, opcode, ft, offset, base='sp'):
        self.emit(opcode << 26 | REG[base] << 21 | ft << 16 | (offset & 65535))

    def int_to_float(self, rt, fd=0):
        self.emit(17 << 26 | 4 << 21 | REG[rt] << 16 | fd << 11)  # mtc1
        self.emit(17 << 26 | 20 << 21 | fd << 11 | fd << 6 | 32)  # cvt.s.w

    def add_float(self, fd, fs, ft):
        self.emit(17 << 26 | 16 << 21 | ft << 16 | fs << 11 | fd << 6)

    def ret(self):
        self.emit(REG['ra'] << 21 | 8)
        self.emit(0)

    def finish(self, table):
        self.label('table')
        for index, kind, target in self.fixups:
            address = CODE_VA + self.labels[target] if isinstance(target, str) else target
            if kind == 'branch':
                value = (address - (CODE_VA + index * 4 + 4)) // 4
                if not -32768 <= value <= 32767:
                    raise ValueError('Branch out of range')
                self.words[index] |= value & 65535
            elif kind == 'jump':
                self.words[index] |= address >> 2
            elif kind == 'hi':
                self.words[index] |= ((address + 0x8000) >> 16) & 65535
            else:
                self.words[index] |= address & 65535
        return struct.pack('<%dI' % len(self.words), *self.words) + table


def compile_hooks(metrics):
    # Keyed by little-endian CP932 unit, not by Unicode or ASCII.
    entries = sorted((int.from_bytes(bytes.fromhex(row['cp932_hex']), 'little'),
                      row['proposed_advance_pixels'],
                      3 - row['ink_bounds_inclusive'][0] if row['ink_bounds_inclusive'] else 3)
                     for row in metrics['characters'].values())
    if len({e[0] for e in entries}) != len(entries):
        raise ValueError('Ambiguous font code')
    table = b''.join(struct.pack('<HBb', *entry) for entry in entries)
    a = Assembler()
    a.label('glyph')
    a.i(9, 'sp', 'sp', -32)
    for register, offset in [('ra', 28), ('a0', 0), ('a1', 4), ('a2', 8)]:
        a.i(43, register, 'sp', offset)
    a.branch(5, 's0', 'zero', 'glyph_original')  # Preserve non-default styles.
    a.i(37, 'a0', 'a1', 0)
    a.jump('lookup')
    a.branch(4, 'v0', 'zero', 'glyph_original')
    a.int_to_float('v1')
    for offset in (0x50 + 32, 0x58 + 32):
        a.fp_mem(49, 2, offset)
        a.add_float(2, 2, 0)
        a.fp_mem(57, 2, offset)
    a.int_to_float('v0')
    a.fp_mem(57, 0, 0x48 + 32)
    a.label('glyph_original')
    for register, offset in [('a0', 0), ('a1', 4), ('a2', 8), ('ra', 28)]:
        a.i(35, register, 'sp', offset)
    a.i(9, 'sp', 'sp', 32)
    a.jump(0x682e8, link=False)

    a.label('measure')
    a.i(9, 'sp', 'sp', -32)
    for register, offset in [('ra', 28), ('a0', 0), ('a1', 4)]:
        a.i(43, register, 'sp', offset)
    a.jump(0x685cc)
    a.i(35, 't0', 'sp', 4)
    a.branch(5, 't0', 'zero', 'measure_return')
    a.i(37, 'a0', 's2', 0)
    a.jump('lookup')
    a.branch(4, 'v0', 'zero', 'measure_return')
    # Original caller adds the returned float to its fixed 16-pixel width.
    a.i(9, 'v0', 'v0', -16)
    a.branch(5, 's1', 's4', 'measure_store')
    a.i(9, 'v0', 'v0', 2)  # Three-pixel left inset minus final one-pixel advance gap.
    a.label('measure_store')
    a.int_to_float('v0')
    a.i(35, 'a0', 'sp', 0)
    a.fp_mem(57, 0, 0, base='a0')
    a.label('measure_return')
    for register, offset in [('a0', 0), ('a1', 4), ('ra', 28)]:
        a.i(35, register, 'sp', offset)
    a.i(9, 'sp', 'sp', 32)
    a.ret()

    a.label('lookup')
    a.table_address('t0')
    a.i(9, 't1', 'zero', len(entries))
    a.label('lookup_loop')
    a.i(37, 't2', 't0', 0)
    a.branch(4, 'a0', 't2', 'lookup_found')
    a.i(9, 't0', 't0', 4)
    a.i(9, 't1', 't1', -1)
    a.branch(5, 't1', 'zero', 'lookup_loop')
    a.move('v0', 'zero')
    a.ret()
    a.label('lookup_found')
    a.i(36, 'v0', 't0', 2)
    a.i(32, 'v1', 't0', 3)
    a.ret()
    compile_pool_hooks(a)
    code = a.finish(table)
    return code, a.labels, a.relocs


def compile_pool_hooks(a):
    # Only the dialogue controller's call sites are redirected. Its embedded
    # 64-object array remains intact for original parent reset/release loops.
    saved = [('s0', 32), ('s1', 36), ('s2', 40), ('ra', 60)]

    def prologue(label):
        a.label(label)
        a.i(9, 'sp', 'sp', -64)
        for reg, offset in saved:
            a.i(43, reg, 'sp', offset)
        a.move('s0', 'a0')

    def epilogue():
        for reg, offset in saved:
            a.i(35, reg, 'sp', offset)
        a.i(9, 'sp', 'sp', 64)
        a.ret()

    prologue('pool_bind')
    # Raw operator-new storage, not the array allocator with a hidden cookie.
    a.i(13, 'a0', 'zero', FONT_POOL_CAPACITY * FONT_OBJECT_BYTES)
    a.jump(0x1ea6cc)
    a.move('s1', 'v0')
    a.branch(4, 's1', 'zero', 'pool_allocation_failed')
    a.i(43, 's1', 'sp', 48)
    a.move('s2', 'zero')
    a.label('pool_construct_loop')
    a.move('a0', 's1')
    a.jump(0x1cba50)
    a.i(9, 's1', 's1', FONT_OBJECT_BYTES)
    a.i(9, 's2', 's2', 1)
    a.i(11, 't0', 's2', FONT_POOL_CAPACITY)
    a.branch(5, 't0', 'zero', 'pool_construct_loop')
    a.move('a0', 's0')
    a.i(35, 'a1', 'sp', 48)
    a.i(13, 'a2', 'zero', FONT_POOL_CAPACITY)
    a.jump(0x68a2c)
    epilogue()

    prologue('pool_release')
    a.i(35, 't0', 's0', 0x34)
    a.i(13, 't1', 'zero', FONT_POOL_CAPACITY)
    a.branch(5, 't0', 't1', 'pool_release_done')
    a.i(35, 's1', 's0', 0x30)
    a.branch(4, 's1', 'zero', 'pool_allocation_failed')
    a.i(43, 's1', 'sp', 48)
    a.move('a0', 's0')
    a.jump(0x68b00)  # Release cached glyphs and clear referencing glyph records.
    a.move('s2', 'zero')
    a.label('pool_destruct_loop')
    a.move('a0', 's1')
    a.move('a1', 'zero')  # Destruct each element without individually freeing it.
    a.jump(0x1cba8c)
    a.i(9, 's1', 's1', FONT_OBJECT_BYTES)
    a.i(9, 's2', 's2', 1)
    a.i(11, 't0', 's2', FONT_POOL_CAPACITY)
    a.branch(5, 't0', 'zero', 'pool_destruct_loop')
    a.i(35, 'a0', 'sp', 48)
    a.jump(0x1ea718)
    a.i(43, 'zero', 's0', 0x30)
    a.i(43, 'zero', 's0', 0x34)
    a.label('pool_release_done')
    epilogue()

    for label, target in [('pool_reset', 0x68710), ('pool_close', 0x68ac4)]:
        a.label(label)
        a.i(9, 'sp', 'sp', -32)
        a.i(43, 'a0', 'sp', 16)
        a.i(43, 'ra', 'sp', 28)
        a.jump('pool_release')
        a.i(35, 'a0', 'sp', 16)
        a.i(35, 'ra', 'sp', 28)
        a.i(9, 'sp', 'sp', 32)
        a.jump(target, link=False)

    a.label('pool_allocation_failed')
    a.emit(0x0000000d)  # Fail at a known trap; never use a null/undersized pool.
    a.branch(4, 'zero', 'zero', 'pool_allocation_failed')


def build_patch():
    original = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    if sha(original) != ELF_SHA256:
        raise ValueError('Executable source hash differs')
    metrics, _ = collect()
    code, labels, extra_relocs = compile_hooks(metrics)
    phoff, shoff = struct.unpack_from('<II', original, 28)
    phentsize, phnum, shentsize, shnum = struct.unpack_from('<4H', original, 42)
    if (phoff, phentsize, phnum, shentsize, shnum) != (52, 32, 3, 40, 55):
        raise ValueError('Unexpected source ELF topology')
    phdrs = [list(struct.unpack_from('<8I', original, phoff + i * 32)) for i in range(phnum)]
    sections = [list(struct.unpack_from('<10I', original, shoff + i * 40)) for i in range(shnum)]
    if any(original[phoff + phnum * 32:phoff + (phnum + 1) * 32]):
        raise ValueError('Program-header expansion would overwrite data')
    if align(max(p[2] + p[5] for p in phdrs if p[0] == 1)) != CODE_VA:
        raise ValueError('New code segment would not follow the original allocation')
    rel = phdrs[2]
    if rel[0] != 0x700000a0 or rel[4] % 8:
        raise ValueError('Expected uncompressed PSP relocations')
    old_relocs = original[rel[1]:rel[1] + rel[4]]
    rel_records = [struct.unpack_from('<II', old_relocs, n) for n in range(0, len(old_relocs), 8)]
    out = bytearray(original)
    hooks = []
    for address, (old_target, label) in HOOKS.items():
        instruction = struct.unpack_from('<I', original, address + 0xc0)[0]
        if instruction != (3 << 26 | old_target >> 2) or rel_records.count((address, 4)) != 1:
            raise ValueError('Hook instruction or relocation differs')
        target = CODE_VA + labels[label]
        struct.pack_into('<I', out, address + 0xc0, 3 << 26 | target >> 2)
        hooks.append({'module_address': hex(address), 'original_target': hex(old_target),
                      'new_target': hex(target), 'hook': label})
    code_offset = align(len(out))
    out.extend(bytes(code_offset - len(out)))
    out.extend(code)
    relocation_offset = align(len(out), 16)
    out.extend(bytes(relocation_offset - len(out)))
    out.extend(old_relocs)
    out.extend(b''.join(struct.pack('<II', *r) for r in extra_relocs))
    for section in sections:
        if section[1] == 0x700000a0:
            if not rel[1] <= section[4] < section[4] + section[5] <= rel[1] + rel[4]:
                raise ValueError('Relocation section outside the original segment')
            section[4] += relocation_offset - rel[1]
    sections.append([0, 1, 6, CODE_VA, code_offset, len(code), 0, 0, 64, 0])
    sections.append([0, 0x700000a0, 0, 0, relocation_offset + len(old_relocs),
                     len(extra_relocs) * 8, 52, shnum, 4, 8])
    new_shoff = align(len(out), 16)
    out.extend(bytes(new_shoff - len(out)))
    out.extend(b''.join(struct.pack('<10I', *s) for s in sections))
    rel[1], rel[4] = relocation_offset, len(old_relocs) + len(extra_relocs) * 8
    phdrs.append([1, code_offset, CODE_VA, 0, len(code), len(code), 5, 64])
    for i, p in enumerate(phdrs):
        struct.pack_into('<8I', out, phoff + i * 32, *p)
    struct.pack_into('<I', out, 32, new_shoff)
    struct.pack_into('<H', out, 44, len(phdrs))
    struct.pack_into('<H', out, 48, len(sections))
    allowed = set(range(32, 36)) | set(range(44, 46)) | set(range(48, 50))
    allowed |= set(range(phoff + 2 * 32, phoff + 4 * 32))
    for address in HOOKS:
        allowed.update(range(address + 0xc0, address + 0xc0 + 4))
    if any(out[n] != original[n] for n in range(len(original)) if n not in allowed):
        raise ValueError('Unexpected original executable byte changed')
    report = {'profile': PROFILE, 'source_elf_sha256': ELF_SHA256,
              'patched_elf_sha256': sha(out), 'source_bytes': len(original), 'patched_bytes': len(out),
              'added_segment_index': 3, 'added_segment_module_address': hex(CODE_VA),
              'added_segment_file_offset': code_offset, 'added_segment_bytes': len(code),
              'added_segment_sha256': sha(code), 'extra_relocation_records': extra_relocs,
              'original_relocation_records_preserved': len(rel_records), 'hooks': hooks,
              'labels': labels, 'supported_characters': len(metrics['characters']),
              'font_resource_sha256': metrics['font_resource_sha256'],
              'metrics_policy': metrics['spacing_policy'],
              'nondefault_glyph_styles_preserved': True,
              'unmapped_characters_preserved': True,
              'font_pool': {'capacity': FONT_POOL_CAPACITY, 'object_bytes': FONT_OBJECT_BYTES,
                            'allocation_bytes': FONT_POOL_CAPACITY * FONT_OBJECT_BYTES,
                            'ownership': 'One separate heap allocation per active dialogue context',
                            'allocator_module_address': '0x1ea6cc', 'free_module_address': '0x1ea718',
                            'constructor_module_address': '0x1cba50', 'destructor_module_address': '0x1cba8c',
                            'reset_and_close_release_owned_pool': True,
                            'original_embedded_pool_preserved': True},
              'scope_limit': 'Dialogue geometry and width for mapped Latin, default glyph style. Runtime validation and hardware compatibility still required.'}
    return bytes(out), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'work/scratch/font_patch_01')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents:
        raise ValueError('Output must stay inside the workspace')
    patched, report = build_patch()
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'output': str(output), 'report': report}, indent=2))
    if args.write:
        output.mkdir()  # Refuse existing evidence.
        (output / 'EBOOT.elf').write_bytes(patched)
        (output / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
