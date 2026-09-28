"""Measure existing Latin glyph ink from the verified game font; preview first."""
import argparse
import hashlib
import json
import struct

from dialogue_encoding import encode_dialogue
from sn3_archive import GameSource, ROOT

ELF_SHA256 = '82cc184377986d90d298ee4918fb11bd0e3524659e5c6f8b7b3c859f4d232684'
FONT_SHA256 = '0db773359358341c6d4f235d6db74fd1096e0dd5164ab199adbaf8a4845af9e2'
MAP_VA = 0x226000
ELF_SEGMENT_OFFSET = 0xc0
FONT_SOURCES = [('00.DAT', 37284080), ('02.DAT', 456704)]
FONT_SIZE = 473088


def digest(data):
    return hashlib.sha256(data).hexdigest()


def collect():
    elf = (ROOT / 'work/source/EBOOT.elf').read_bytes()
    if digest(elf) != ELF_SHA256:
        raise ValueError('Font mapping requires the verified source executable')
    source = GameSource()
    try:
        copies = [source.read(bank, offset, FONT_SIZE) for bank, offset in FONT_SOURCES]
    finally:
        source.stream.close()
    if any(digest(data) != FONT_SHA256 for data in copies):
        raise ValueError('A source font copy differs from the verified resource')
    font = copies[0]
    bpp = struct.unpack_from('<I', font, 0x10)[0]
    width, height = struct.unpack_from('<HH', font, 0x14)
    payload_size = struct.unpack_from('<I', font, 0x18)[0]
    if font[:4] != b'BIT\0' or (bpp, width, height) != (4, 16, 16):
        raise ValueError('Unexpected font header')
    glyph_bytes = width * height // 2
    if payload_size % glyph_bytes or 28 + payload_size > len(font):
        raise ValueError('Invalid font payload bounds')
    metrics, rejected = {}, {}
    for codepoint in range(32, 127):
        char = chr(codepoint)
        try:
            encoded, _ = encode_dialogue(char, char)
        except (ValueError, UnicodeError) as exc:
            rejected[char] = str(exc)
            continue
        lead, trail = encoded
        if not 0x80 <= lead <= 0xff or not 0x40 <= trail <= 0xff:
            raise ValueError('Character is outside the mapped two-byte font lookup')
        page = struct.unpack_from('<I', elf, ELF_SEGMENT_OFFSET + MAP_VA + (lead - 0x80) * 4)[0]
        if not page or page + ELF_SEGMENT_OFFSET + (trail - 0x40) * 2 + 2 > len(elf):
            rejected[char] = 'No verified font mapping page'
            continue
        index = struct.unpack_from('<H', elf, ELF_SEGMENT_OFFSET + page + (trail - 0x40) * 2)[0]
        if not 1 <= index <= payload_size // glyph_bytes:
            rejected[char] = 'No mapped glyph; native fallback is not accepted'
            continue
        offset = 28 + (index - 1) * glyph_bytes
        bitmap = font[offset:offset + glyph_bytes]
        pixels = [(x, y) for y in range(height) for x in range(width)
                  if (bitmap[(y * width + x) // 2] >> (4 * (x % 2))) & 15]
        bounds = ([min(x for x, _ in pixels), min(y for _, y in pixels),
                   max(x for x, _ in pixels), max(y for _, y in pixels)] if pixels else None)
        if not bounds and char != ' ':
            rejected[char] = 'Mapped glyph is blank'
            continue
        metrics[char] = {'cp932_hex': encoded.hex(), 'glyph_index': index,
                         'font_byte_offset': offset, 'glyph_sha256': digest(bitmap),
                         'ink_bounds_inclusive': bounds,
                         'proposed_advance_pixels': bounds[2] - bounds[0] + 2 if bounds else 5,
                         'proposed_center_offset_pixels': 8 - bounds[0] if bounds else 8}
    result = {'schema_version': 1, 'profile': 'existing_latin_ink_spacing_experiment_v1',
              'status': 'Measured source ink; advances are a proposed policy, not a production font patch.',
              'source_elf_sha256': ELF_SHA256, 'font_resource_sha256': FONT_SHA256,
              'font_resources': ['00:00044/00004/00000', '02:00004/00000'],
              'map_module_address': hex(MAP_VA), 'glyph_dimensions': [width, height],
              'bits_per_pixel': bpp, 'nibble_order': 'low nibble is the left pixel',
              'font_payload_bytes': payload_size, 'font_glyph_count': payload_size // glyph_bytes,
              'native_glyph_draw_size_unchanged': True,
              'spacing_policy': 'One blank pixel after inclusive ink bounds; ordinary space advances five pixels.',
              'characters': metrics, 'rejected_characters': rejected,
              'tool_sha256': digest((ROOT / 'tools/font_metrics.py').read_bytes())}
    return result, font[:28 + payload_size]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report, _ = collect()
    destination = ROOT / 'work/ui/latin_font_metrics.json'
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'mapped_characters': len(report['characters']),
                      'rejected_characters': report['rejected_characters'],
                      'font_glyph_count': report['font_glyph_count'],
                      'samples': {c: report['characters'][c] for c in ' Ei.mW?'},
                      'scope': report['status']}, indent=2))
    if args.write:
        with destination.open('x', encoding='utf-8') as output:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
