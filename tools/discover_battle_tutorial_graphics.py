"""Decode an explicit static-texture ID range into a new discovery contact sheet.

The default range is the compact 480x272 sequence in 02.DAT selected for
battle/tutorial artwork inspection.  A dry run verifies every source payload;
--write is required to create the destination.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from sn3_archive import ROOT, GameSource
from sn3_ui_textures import decode_texture, texture_records


def digest(data):
    return hashlib.sha256(data).hexdigest()


def selected(index, first, last):
    result = []
    for group in index['resources']:
        hits = [o for o in group['occurrences']
                if o['bank'] == '02.DAT' and len(o['path']) == 1 and first <= o['path'][0] <= last]
        if hits:
            result.append((group, hits[0]))
    return sorted(result, key=lambda row: row[1]['path'][0])


def collect(first, last):
    index_path = ROOT / 'work/ui/interface_graphics.index.json'
    index_raw = index_path.read_bytes()
    index = json.loads(index_raw)
    items, skipped = [], []
    with GameSource() as source:
        for group, occurrence in selected(index, first, last):
            data = source.read(occurrence['bank'], occurrence['offset'], occurrence['size'])
            if digest(data) != occurrence['sha256'] or occurrence['sha256'] != group['source_sha256']:
                raise ValueError('Source payload hash changed: ' + occurrence['id'])
            rows = texture_records(data)
            for row in rows:
                identity = occurrence['id'] + ':sprite:%03d' % row['number']
                try:
                    image = decode_texture(data, row)
                except ValueError as exc:
                    skipped.append({'id': identity, 'width': row['width'], 'height': row['height'],
                                    'format': row['format'], 'swizzled': row['swizzled'], 'reason': str(exc)})
                    continue
                items.append(({'id': identity, 'resource_id': occurrence['id'],
                               'source_sha256': occurrence['sha256'], 'width': row['width'],
                               'height': row['height'], 'format': row['format'],
                               'swizzled': row['swizzled'], 'texture_number': row['number'],
                               'pixel_storage_sha256': digest(data[row['data_offset']:row['data_offset'] + row['data_size']])}, image))
    return {'source_catalog': 'work/ui/interface_graphics.index.json',
            'source_catalog_sha256': digest(index_raw),
            'id_range': {'bank': '02.DAT', 'first': first, 'last': last},
            'resource_count': len({x[0]['resource_id'] for x in items}),
            'texture_count': len(items), 'skipped_texture_count': len(skipped),
            'skipped_textures': skipped}, items


def export(destination, report, items):
    destination.mkdir(parents=True, exist_ok=False)
    records = []
    for record, image in items:
        name = record['id'].replace(':', '_').replace('/', '_') + '.png'
        path = destination / name
        image.save(path)
        records.append({**record, 'image_file': name, 'image_sha256': digest(path.read_bytes())})
    page = Image.new('RGB', (1440, ((len(items) + 3) // 4) * 220), (185, 185, 185))
    draw = ImageDraw.Draw(page)
    for slot, (record, image) in enumerate(items):
        x, y = slot % 4 * 360, slot // 4 * 220
        draw.text((x + 4, y + 3), record['id'], fill=(0, 0, 0))
        preview = image.copy()
        preview.thumbnail((352, 190))
        page.paste(preview, (x + 4, y + 22), preview)
    sheet = 'contact_all.jpg'
    page.save(destination / sheet, quality=92)
    report.update({'contact_sheet': sheet, 'contact_sheet_scope': 'Every decoded texture in the explicit source ID range.',
                   'textures': records})
    (destination / 'index.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first', type=int, default=3892)
    parser.add_argument('--last', type=int, default=3924)
    parser.add_argument('--destination', default='work/ui/battle_0.1.13/discovery/fullpage_03892_03924')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    destination = (ROOT / args.destination).resolve()
    if ROOT not in destination.parents or (args.write and destination.exists()):
        parser.error('Destination must be a new directory within the workspace')
    report, items = collect(args.first, args.last)
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      **report, 'sample': [record for record, image in items[:3]]}, indent=2))
    if args.write:
        export(destination, report, items)


if __name__ == '__main__':
    main()
