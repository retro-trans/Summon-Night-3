"""Decode native UI sprite textures for source identification; preview before export."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from sn3_archive import GameSource, ROOT, parse_index, child
from sn3_codec import decoded_size, decompress


def digest(data):
    return hashlib.sha256(data).hexdigest()


def texture_records(data):
    if data[:8] != bytes.fromhex('0100000001112100'):
        raise ValueError('Not a supported static texture resource')
    base, palette_base = struct.unpack_from('<II', data, 0x14)
    if not 32 <= base < len(data) - 4:
        raise ValueError('Texture directory is out of bounds')
    count = struct.unpack_from('<I', data, base)[0]
    if not 0 < count <= 512 or base + 4 + count * 32 > len(data):
        raise ValueError('Invalid texture count')
    result = []
    for number in range(count):
        values = struct.unpack_from('<4H4I2H2BH', data, base + 4 + number * 32)
        width, height, tw, th, offset, size, fmt, palette, wp, hp, swizzle, flags, pitch = values
        start = base + offset
        if not (0 < width <= pitch <= 4096 and 0 < height <= 4096
                and start >= base + 4 + count * 32 and start + size <= len(data)):
            raise ValueError('Invalid texture bounds')
        result.append({'number': number, 'width': width, 'height': height,
                       'texture_width': tw, 'texture_height': th, 'pitch': pitch,
                       'data_offset': start, 'data_size': size, 'format': fmt,
                       'palette': palette, 'palette_base': palette_base,
                       'swizzled': swizzle, 'flags': flags,
                       'descriptor_offset': base + 4 + number * 32})
    return result


def decode_texture(data, row):
    from PIL import Image
    fmt, pitch, height = row['format'], row['pitch'], row['height']
    if fmt not in (4, 5) or row['swizzled'] not in (0, 1):
        raise ValueError('Only verified indexed 4/8-bit texture formats are supported')
    row_bytes = pitch if fmt == 5 else (pitch + 1) // 2
    stored_height, remainder = divmod(row['data_size'], row_bytes)
    if remainder or stored_height not in (height, height + 8):
        raise ValueError('Pixel storage does not match the visible height or one guard block')
    start = row['data_offset']
    pixels = data[start:start + row['data_size']]
    if row['swizzled']:
        if row_bytes % 16 or stored_height % 8:
            raise ValueError('Swizzled texture lacks complete 16-byte by 8-row blocks')
        linear = bytearray(len(pixels))
        for y in range(stored_height):
            for x in range(0, row_bytes, 16):
                source = ((y // 8) * (row_bytes // 16) + x // 16) * 128 + (y % 8) * 16
                linear[y * row_bytes + x:y * row_bytes + x + 16] = pixels[source:source + 16]
        pixels = linear
    pal_base = row['palette_base']
    if not 0 <= pal_base <= len(data) - 32:
        raise ValueError('Palette directory is out of bounds')
    count = struct.unpack_from('<I', data, pal_base)[0]
    if count != 1 or row['palette'] != 0:
        raise ValueError('Multiple palette layout is not yet verified')
    offset, size, pal_fmt, colors = struct.unpack_from('<4I', data, pal_base + 4)
    if pal_fmt != 3 or size != colors * 4 or colors not in (16, 256):
        raise ValueError('Palette is not a bounded RGBA8888 palette')
    palette = data[pal_base + offset:pal_base + offset + size]
    if len(palette) != size:
        raise ValueError('Palette exceeds the resource')
    indices = pixels if fmt == 5 else [value for byte in pixels for value in (byte & 15, byte >> 4)]
    if max(indices) >= colors:
        raise ValueError('Pixel references outside palette')
    rgba = bytes(component for index in indices for component in palette[index * 4:index * 4 + 4])
    return Image.frombytes('RGBA', (pitch, stored_height), rgba).crop((0, 0, row['width'], height))


def collect(numbers):
    images, records, skipped, resources = [], [], [], []
    with GameSource() as source:
        for number in numbers:
            raw = source.resource('02.DAT', number)
            data, compressed = raw, False
            try:
                if 0 < decoded_size(raw) <= 16 * 1024 * 1024:
                    data, used = decompress(raw, 0x9831, 16 * 1024 * 1024)
                    if any(raw[used:]):
                        raise ValueError('Nonzero compressed tail')
                    compressed = True
            except ValueError:
                data = raw
            pack = parse_index(data, len(data))
            resources.append({'id': '02:%05d' % number, 'source_sha256': digest(raw),
                              'decoded_sha256': digest(data), 'compressed_key': '0x9831' if compressed else None,
                              'children': pack['count']})
            for entry in pack['entries']:
                identity = '02:%05d/%05d' % (number, entry['id'])
                payload = child(data, pack, entry['id'])
                if not payload:
                    continue
                try:
                    rows = texture_records(payload)
                except ValueError as exc:
                    skipped.append({'id': identity, 'reason': str(exc), 'header_hex': payload[:16].hex()})
                    continue
                for row in rows:
                    record = {'id': identity + ':sprite:%03d' % row['number'],
                              'resource_id': identity, 'source_sha256': digest(payload),
                              'resource_offset_in_pack': entry['offset'],
                              'offset_space': 'decoded_pack' if compressed else 'raw_pack', **row}
                    try:
                        image = decode_texture(payload, row)
                    except ValueError as exc:
                        skipped.append({'id': record['id'], 'reason': str(exc)})
                        continue
                    filename = record['id'].replace(':', '_').replace('/', '_') + '.png'
                    record['image_file'] = filename
                    records.append(record)
                    images.append((record, image))
    return {'schema_version': 1, 'scope': 'Selected related UI packs; decoded source graphics, not translated images.',
            'resources': resources, 'textures': records, 'skipped': skipped}, images


def export(destination, report, images):
    from PIL import Image, ImageDraw
    destination.mkdir(parents=True, exist_ok=False)
    for record, image in images:
        path = destination / record['image_file']
        image.save(path)
        record['image_sha256'] = digest(path.read_bytes())
    contact_images, seen = [], set()
    for record, image in images:
        key = (image.size, digest(image.tobytes()))
        if key not in seen and (image.width > 32 or image.height > 64):
            contact_images.append((record, image))
            seen.add(key)
    report['contact_sheet_scope'] = 'Unique decoded images wider than 32 or taller than 64 pixels; all individual images remain indexed.'
    report['contact_image_count'] = len(contact_images)
    pages = []
    for page_number, start in enumerate(range(0, len(contact_images), 24)):
        page = Image.new('RGB', (1440, 6 * 190), (185, 185, 185))
        draw = ImageDraw.Draw(page)
        for slot, (record, image) in enumerate(contact_images[start:start + 24]):
            x, y = slot % 4 * 360, slot // 4 * 190
            draw.text((x + 4, y + 3), record['id'], fill=(0, 0, 0))
            preview = image.copy()
            preview.thumbnail((352, 166))
            page.paste(preview, (x + 4, y + 20), preview)
        name = 'contact_%02d.jpg' % page_number
        page.save(destination / name, quality=92)
        pages.append(name)
    report['contact_sheets'] = pages
    (destination / 'index.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packs', default='4,27,28,29,30,31,32,33')
    parser.add_argument('--destination', default='work/ui/setup_assets')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    destination = (ROOT / args.destination).resolve()
    if ROOT not in destination.parents or (args.write and destination.exists()):
        parser.error('Destination must be a new directory within the workspace')
    report, images = collect([int(number) for number in args.packs.split(',')])
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'resources': report['resources'], 'texture_count': len(images),
                      'sample': report['textures'][:3], 'skipped_count': len(report['skipped']),
                      'skipped_examples': report['skipped'][:8]}, indent=2))
    if args.write:
        export(destination, report, images)


if __name__ == '__main__':
    main()
