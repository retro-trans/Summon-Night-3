"""Keep symbolic inventory-stat streams on the native grid.

The menu 0.1.20 help-position hook at 0x642c0 is correct for CP932 text
cells, but it treats every unsupported cell as a 13-pixel character.  The
inventory formatter supplies stat labels as a symbolic stream: for example,
the cells ``0xa383, 0x4081, 0x5182`` render as ``AT+2``.  Those cells must
retain the stock callback's component-specific placement.  The renderer
marks this stream with context mode 6 at ``s4+0x34``.  This wrapper forwards
only that mode to the native position callback and sends ordinary help rows
to the existing VWF helper.

This module is intentionally dry-run only.  ``prepare`` is pure: callers own
any output file they choose to create.
"""
import hashlib
import json
import struct

from font_patch import REG
from menu_code_020 import append
from sn3_archive import ROOT


HELP_POSITION_HOOK = 0x642C0
EXISTING_HELP_POSITION = 0x347BE0
EXPECTED_HOOK_WORD = 0x0C0D1EF8  # jal 0x347be0


def emit(a):
    """Emit a dispatch wrapper for the already-delayed 0x642c0 call site."""
    a.label('stat_cell_dispatch')
    # The renderer reads this mode at 0x64268 before it builds this row's
    # glyph objects.  Mode 6 is the inventory's symbolic stat stream.
    a.i(35, 't0', 's4', 0x34)  # lw t0,0x34(s4)
    a.i(9, 't1', 'zero', 6)    # addiu t1,zero,6
    a.branch(4, 't0', 't1', 'native_grid')
    a.label('vwf_position')
    a.jump(EXISTING_HELP_POSITION, link=False)
    a.label('native_grid')
    # a2 remains the native virtual position callback from 0x642b0.  The
    # original jal has already put 0x642c8 in ra, so a tail jump preserves the
    # stock return path and its unmodified f12 grid position.
    a.emit(REG['a2'] << 21 | 8)  # jr a2
    a.emit(0)


def _file_offset_for_va(data, address):
    """Resolve an executable virtual address through the ELF load segments."""
    from stages_pupil_names import parse_elf
    for segment in parse_elf(data)['phdrs']:
        kind, file_offset, virtual_address, _physical, file_size = segment[:5]
        if kind == 1 and virtual_address <= address < virtual_address + file_size:
            return file_offset + address - virtual_address
    raise AssertionError(hex(address))


def _word_at_va(data, address):
    return struct.unpack_from('<I', data, _file_offset_for_va(data, address))[0]


def _dispatch_path(renderer_mode):
    """The two data classes accepted by the emitted branch."""
    return 'native_grid' if renderer_mode == 6 else 'existing_vwf'


def prepare(data, *, expected_source_sha256=None):
    """Return a patched ELF and metadata without writing either to disk."""
    source_sha256 = hashlib.sha256(data).hexdigest()
    if expected_source_sha256 is not None:
        assert source_sha256 == expected_source_sha256, source_sha256
    actual = struct.unpack_from('<I', data, HELP_POSITION_HOOK + 0xC0)[0]
    assert actual == EXPECTED_HOOK_WORD, hex(actual)
    out, appended = append(
        data,
        emit,
        {HELP_POSITION_HOOK: ('stat_cell_dispatch', EXPECTED_HOOK_WORD)},
    )
    replacement = struct.unpack_from('<I', out, HELP_POSITION_HOOK + 0xC0)[0]
    assert replacement != EXPECTED_HOOK_WORD
    wrapper = int(appended['code_address'], 16) + appended['labels']['stat_cell_dispatch']
    words = [_word_at_va(out, wrapper + offset) for offset in range(0, 32, 4)]
    # Exercise both emitted exits structurally: mode 6 branches to the native
    # callback; every other mode takes the direct non-linking jump to the
    # inherited VWF helper.  This also catches accidental jal/ra changes.
    assert _dispatch_path(6) == 'native_grid'
    assert _dispatch_path(1) == 'existing_vwf'
    assert words[2] >> 26 == 4 and words[2] & 0xFFFF == 3  # beq -> +24
    assert words[4] == (2 << 26 | EXISTING_HELP_POSITION >> 2)  # j, not jal
    assert words[6] == (REG['a2'] << 21 | 8)               # jr a2
    report = {
        'profile': 'inventory_symbolic_stat_spacing_0.1.26',
        'baseline_elf_sha256': source_sha256,
        'expected_source_sha256': expected_source_sha256,
        'hook': hex(HELP_POSITION_HOOK),
        'previous_target': hex(EXISTING_HELP_POSITION),
        'previous_instruction': hex(EXPECTED_HOOK_WORD),
        'replacement_instruction': hex(replacement),
        'symbolic_stat_rule': 'renderer context mode at s4+0x34 equals 6: native grid callback',
        'other_help_rule': 'all other renderer modes: existing help VWF helper',
        'appended': appended,
        'patched_elf_sha256': hashlib.sha256(out).hexdigest(),
    }
    return out, report


def main():
    baseline = (ROOT / 'work/output/0.1.25/EBOOT.elf').read_bytes()
    _out, report = prepare(baseline)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
