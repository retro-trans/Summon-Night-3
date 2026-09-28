"""Append script translations and rewrite verified 20-bit pool references."""
import struct
from script_strings import parse_pool
from sn3_vm import instructions
from dialogue_encoding import encode_dialogue


def relocate_script(data, targets):
    """Targets map original source byte offsets to text and source_sha256.

    Original pool bytes are retained. Runtime allocation is a separate build
    gate: a successful byte-level relocation makes no memory/layout claim.
    """
    parsed = parse_pool(data)
    known = {row['source_offset']: row for row in parsed['strings']}
    if set(targets) - set(known):
        raise ValueError('Target refers to an unknown source string')
    out = bytearray(data)
    changes = []
    for old in sorted(targets):
        target, row = targets[old], known[old]
        if target['source_sha256'] != row['source_sha256']:
            raise ValueError('Source hash mismatch at 0x%x' % old)
        text = target['text']
        profile = target.get('encoding_profile', 'cp932')
        if profile == 'dialogue_fullwidth_cp932':
            source_text = data[old:old + row['source_byte_length']].decode('cp932')
            encoded, display_text = encode_dialogue(text, source_text)
        elif profile == 'cp932':
            encoded, display_text = text.encode('cp932', 'strict'), text
        else:
            raise ValueError('Unknown target encoding profile: ' + profile)
        if not encoded or any(b < 32 for b in encoded):
            raise ValueError('Script strings must be nonempty and contain no raw control bytes')
        if encoded.decode('cp932') != display_text:
            raise ValueError('Target does not round-trip through CP932')
        references = row['reference_instructions']
        if not references:
            raise ValueError('Target has no verified instruction references')
        out.extend(bytes(len(out) % 2))
        new = len(out)
        word_offset = (new - parsed['pool_offset']) // 2
        if word_offset >= 1 << 20:
            raise ValueError('New string exceeds the VM 20-bit word-offset range')
        out.extend(encoded + b'\0')
        # The dialogue reader checks a 16-bit terminator; retain aligned zero
        # padding even for the final appended string, not just before the next.
        out.extend(bytes(len(out) % 2))
        for position in references:
            instruction = struct.unpack_from('<H', data, position)[0]
            struct.pack_into('<HH', out, position,
                             (instruction & 0x0fff) | ((word_offset >> 16) << 12),
                             word_offset & 0xffff)
        changes.append({'old_offset': old, 'new_offset': new, 'text': text,
                        'display_text': display_text, 'encoding_profile': profile,
                        'source_sha256': row['source_sha256'],
                        'old_byte_length': row['source_byte_length'], 'new_byte_length': len(encoded),
                        'pool_word_offset': word_offset, 'reference_instructions': references})
    if out[parsed['pool_offset']:len(data)] != data[parsed['pool_offset']:]:
        raise ValueError('Original pool changed during relocation')
    before = instructions(data)
    after = instructions(out)
    rewritten = {position for change in changes for position in change['reference_instructions']}
    for old, new in zip(before, after):
        if old['offset'] not in rewritten and old != new:
            raise ValueError('Unmodified instruction changed')
        if (old['offset'], old['size'], old['opcode'], old['mode']) != (
                new['offset'], new['size'], new['opcode'], new['mode']):
            raise ValueError('Instruction boundary changed')
    if len(before) != len(after):
        raise ValueError('Instruction count changed')
    verified = parse_pool(out)
    by_offset = {row['source_offset']: row for row in verified['strings']}
    for change in changes:
        if by_offset[change['new_offset']]['reference_instructions'] != change['reference_instructions']:
            raise ValueError('Relocated references did not resolve to the new string')
    return bytes(out), changes
