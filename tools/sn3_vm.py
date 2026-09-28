"""Instruction boundaries for the original script VM, verified from its ELF handlers."""
import struct

HANDLER_TABLE_VA = 0x22a3f8
DISPATCH_VA = 0x1e8050
READ_VALUE_VA = 0x1e82a0
READ_WIDTHS = {0: 1, 1: 1, 2: 1, 3: 2, 4: 1, 5: 1, 6: 0, 7: 0, 8: 0, 9: 1, 10: 0}
WRITE_WIDTHS = {0: 1, 1: 1, 2: 1, 6: 0, 7: 0, 8: 0}
CONTROL_OPS = {7: 'call', 10: 'jump', 11: 'jump_if_true', 12: 'jump_if_false'}


def instructions(data):
    pool = struct.unpack_from('<I', data, 20)[0] * 2
    if not 32 <= pool <= len(data) or pool % 2:
        raise ValueError('Invalid instruction range')
    position = 32
    result = []
    while position < pool:
        word = struct.unpack_from('<H', data, position)[0]
        opcode, mode, high = word & 63, (word >> 6) & 63, word >> 12
        if opcode > 0x22:
            raise ValueError('Unknown opcode at 0x%x: 0x%x' % (position, word))
        if opcode == 5:
            if mode not in READ_WIDTHS:
                raise ValueError('Unknown read mode at 0x%x: %d' % (position, mode))
            following = READ_WIDTHS[mode]
        elif opcode == 6:
            if mode not in WRITE_WIDTHS:
                raise ValueError('Unknown write mode at 0x%x: %d' % (position, mode))
            following = WRITE_WIDTHS[mode]
        elif opcode in (4, 7, 8, 10, 11, 12):
            following = 1
        else:
            following = 0
        end = position + 2 * (1 + following)
        if end > pool:
            raise ValueError('Instruction operand crosses the pool boundary')
        operands = list(struct.unpack_from('<%dH' % following, data, position + 2)) if following else []
        instruction = {'offset': position, 'word': word, 'opcode': opcode, 'mode': mode,
                       'high': high, 'operands': operands, 'size': end - position}
        if opcode == 5 and mode == 4:
            instruction['string_word'] = (high << 16) | operands[0]
        if opcode in CONTROL_OPS:
            instruction['control_kind'] = CONTROL_OPS[opcode]
            instruction['target_word'] = (high << 16) | operands[0]
        result.append(instruction)
        position = end
    return result


def verify_script(data, pool_rows):
    decoded = instructions(data)
    starts = {i['offset'] for i in decoded}
    entry = struct.unpack_from('<I', data, 16)[0] * 2
    if entry not in starts:
        raise ValueError('Entry does not point to an instruction: 0x%x' % entry)
    by_word = {row['pool_word_offset']: row for row in pool_rows}
    references = {word: [] for word in by_word}
    empty_references, extended_references, jumps = 0, 0, 0
    for instruction in decoded:
        if 'target_word' in instruction:
            target = instruction['target_word'] * 2
            if target not in starts:
                raise ValueError('Control target 0x%x from 0x%x is not an instruction' % (target, instruction['offset']))
            jumps += 1
        if 'string_word' in instruction:
            word = instruction['string_word']
            if word == 0:
                empty_references += 1
            elif word not in by_word:
                raise ValueError('Text target 0x%x from 0x%x is not a string start' % (word, instruction['offset']))
            else:
                references[word].append(instruction['offset'])
            extended_references += word > 0xffff
    return {'instruction_count': len(decoded), 'control_references': jumps,
            'empty_string_references': empty_references, 'extended_string_references': extended_references,
            'references': references}
