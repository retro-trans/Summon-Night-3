"""Verify real opening reflow and reject unsafe transformations; preview first."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import struct

from dialogue_layout import PROFILE, PIXEL_PROFILE, layout_dialogue, operand_instruction, wrap_words, wrap_pixels, latin_width
from prepare_opening_layout import prepare
from sn3_archive import GameSource, ROOT
from sn3_codec import compress, decompress
from sn3_vm import instructions


def simulate_group(data, start, stop):
    """Execute emitted instructions, treating queue/display calls as events.

    A sentinel catches argument imbalance. This checks generated code; it does
    not substitute for emulator tests of rendering, timing, or native state.
    """
    decoded = {row['offset']: row for row in instructions(data)}
    pool = struct.unpack_from('<I', data, 20)[0] * 2
    pc, stack, pending, pages, steps = start, ['sentinel'], [], [], 0
    while pc != stop:
        steps += 1
        assert steps < 1000, 'Group did not return to original control flow'
        row = decoded[pc]
        pc += row['size']
        if row['opcode'] == 10:
            pc = row['target_word'] * 2
        elif row['opcode'] == 5:
            if row['mode'] == 4:
                offset = pool + row['string_word'] * 2
                end = offset
                while data[end:end + 2] != b'\0\0':
                    end += 2
                stack.append(data[offset:end].decode('cp932'))
            elif row['mode'] in (5, 9):
                value = (row['high'] << 16) | row['operands'][0]
                stack.append(value - 65536 if row['mode'] == 9 and value >= 32768 else value)
            elif row['mode'] == 10:
                stack.append(row['high'] - 1)
            else:
                raise AssertionError('Unexpected push mode')
        elif row['opcode'] == 7:
            count = row['mode']
            args = stack[-count:] if count else []
            if count:
                del stack[-count:]
            if row['target_word'] == 2003:
                assert len(args) == 1 and isinstance(args[0], str)
                pending.append(args[0])
            else:
                assert pending
                pages.append({'helper': row['target_word'], 'args': args, 'lines': pending})
                pending = []
        else:
            raise AssertionError('Unexpected opcode in group: %d' % row['opcode'])
    assert stack == ['sentinel'] and not pending
    return pages


def verify(profile=PROFILE):
    selection, preview = prepare(profile)
    targets = {row['source_offset']: row for row in selection['translations'].values()}
    with GameSource() as source:
        original = decompress(source.resource('00.DAT', 65), 0xa695)[0]
    updated, changes, groups = layout_dialogue(original, targets, selection['layout_groups'], profile)
    assert decompress(compress(updated, 0xa695), 0xa695)[0] == updated
    for group in groups:
        before = simulate_group(original, *group['original_span'])
        after = simulate_group(updated, *group['original_span'])
        assert len(before) == 1 and len(after) == len(group['pages'])
        for actual, expected in zip(after, group['pages']):
            assert actual['helper'] == before[0]['helper']
            assert actual['args'] == before[0]['args']
            assert actual['lines'] == [row['display_text'] for row in expected]
    old_code = {i['offset']: i for i in instructions(original)}
    new_code = {i['offset']: i for i in instructions(updated)}
    choice_references = set()
    for change in changes:
        if change['old_offset'] in (0x2691a, 0x2692a, 0x26938, 0x26946):
            choice_references.update(change['reference_instructions'])
    for offset, row in old_code.items():
        if 78044 <= offset < 78106 and offset not in choice_references:
            assert new_code[offset] == row
    rejected = []
    def fails(label, action):
        try:
            action()
        except (ValueError, UnicodeError):
            rejected.append(label)
            return
        raise AssertionError('Unsafe case accepted: ' + label)
    first = selection['layout_groups'][0]
    offset = first['source_offsets'][0]
    bad_hash_targets = dict(targets)
    bad_hash_targets[offset] = dict(targets[offset], source_sha256='0' * 64)
    fails('wrong source hash', lambda: layout_dialogue(original, bad_hash_targets, [first]))
    fails('overlapping group ownership', lambda: layout_dialogue(original, targets, [first, dict(first, id='duplicate')]))
    fails('duplicate group ID', lambda: layout_dialogue(original, targets, [first, first]))
    fails('incomplete group', lambda: layout_dialogue(original, targets,
          [{'id': 'partial', 'source_offsets': [0x264a2]}]))
    fails('choice mistaken for dialogue', lambda: layout_dialogue(original, targets,
          [{'id': 'choice', 'source_offsets': [0x2692a]}]))
    fails('word too wide', lambda: wrap_words('unbreakable', 4))
    fails('spacing would be lost', lambda: wrap_words('two  spaces', 14))
    fails('20-bit overflow', lambda: operand_instruction(10, 0, 1 << 20))
    bad_control = bytearray(original)
    branch = next(i for i in instructions(original) if 'target_word' in i)
    bad_control[branch['offset']:branch['offset'] + 4] = operand_instruction(branch['opcode'], branch['mode'], (76240 + 4) // 2)
    fails('branch enters replaced span', lambda: layout_dialogue(bytes(bad_control), targets, [first]))
    bad_line_targets = dict(targets)
    bad_line_targets[offset] = dict(targets[offset], text='bad\nline')
    fails('raw newline', lambda: layout_dialogue(original, bad_line_targets, [first]))
    assert wrap_words('exactly fits', 12) == ['exactly fits']
    assert wrap_words('exactly fits today', 12) == ['exactly fits', 'today']
    if profile == PIXEL_PROFILE:
        from font_metrics import collect
        metrics = collect()[0]['characters']
        fails('pixel width overflow', lambda: wrap_pixels('W' * 13, 208, 31, metrics))
        fails('cell count overflow with narrow ink', lambda: wrap_pixels('i' * 32, 208, 31, metrics))
        fails('unmapped target character', lambda: wrap_pixels('\u2603', 208, 31, metrics))
        fails('pixel wrapping whitespace loss', lambda: wrap_pixels('two  spaces', 208, 31, metrics))
        assert wrap_pixels('i' * 31, 208, 31, metrics) == ['i' * 31]
        exact = latin_width('Wide letters', metrics)
        assert wrap_pixels('Wide letters', exact, 31, metrics) == ['Wide letters']
        assert wrap_pixels('Wide letters', exact - 1, 31, metrics) == ['Wide', 'letters']
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'source_iso_sha256': selection['source_iso_sha256'], 'layout_profile': profile, 'preview': preview,
            'group_execution_checks': len(groups), 'choice_control_flow_preserved': True,
            'compression_roundtrip': True, 'unsafe_cases_rejected': rejected,
            'input_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                            ['tools/dialogue_layout.py', 'tools/prepare_opening_layout.py', 'tools/verify_dialogue_layout.py',
                             'tools/script_repack.py', 'tools/script_strings.py', 'tools/sn3_vm.py', 'tools/dialogue_encoding.py']
                            + (['tools/font_metrics.py'] if profile == PIXEL_PROFILE else [])},
            'scope_limit': 'Static compiler and bounded group execution only; runtime pagination, voices, geometry, branches and save/load require live testing.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--profile', choices=[PROFILE, PIXEL_PROFILE], default=PROFILE)
    args = parser.parse_args()
    result = verify(args.profile)
    destination = ROOT / 'docs' / ('latin_layout_validation_0.1.4.json' if args.profile == PIXEL_PROFILE else 'dialogue_layout_validation.json')
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination), 'report': result}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
