"""Preserve the five user-supplied UI screenshots and measured inspection regions."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from sn3_archive import ROOT

INPUTS = [
    ('options', '239a0ac2-4e55-422b-b060-7a71a3e30e72', [
        ('title', [334, 8, 294, 68]), ('settings', [105, 110, 354, 197]),
        ('help', [122, 392, 720, 31]), ('footer', [280, 469, 419, 32])]),
    ('protagonist', 'bcffc253-6f7e-43d8-a947-c013d3cc83d3', [
        ('heading', [65, 27, 347, 82]), ('confirm', [169, 452, 129, 58])]),
    ('affinity', 'd5e4adcd-8c25-47a6-93a0-0e256cc5bb53', [
        ('heading', [65, 27, 347, 82]), ('affinity', [695, 208, 139, 51]),
        ('description', [561, 271, 372, 205]), ('confirm', [169, 452, 129, 58])]),
    ('name_entry', 'bf3361a0-a1d8-4328-94d3-8f0fa5b3a0fb', [
        ('heading', [80, 28, 292, 71]), ('name_field', [13, 162, 285, 53]),
        ('editing_buttons', [310, 158, 374, 68]), ('keyboard', [79, 245, 808, 212]),
        ('footer', [205, 477, 545, 34])]),
    ('confirmation', 'd72912c4-b449-4ff1-ae58-c0157f416bfa', [
        ('question', [34, 28, 404, 31]), ('yes_no', [183, 68, 90, 70])]),
]


def main():
    from PIL import Image
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    destination = ROOT / 'work/ui/user_setup_screenshots'
    if destination.exists():
        parser.error('Destination already exists; preserve original evidence')
    rows = []
    for number, (name, suffix, regions) in enumerate(INPUTS, 1):
        source = Path('C:/Users/Binh/AppData/Local/Temp/codex-clipboard-' + suffix + '.png')
        with Image.open(source) as image:
            width, height = image.size
        for _, (x, y, w, h) in regions:
            if not (0 <= x < x + w <= width and 0 <= y < y + h <= height):
                raise ValueError('Region exceeds screenshot: ' + name)
        rows.append({'screenshot_number': number, 'screen': name, 'source_path': str(source),
                     'image_file': name + '.png', 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'width': width, 'height': height,
                     'coordinate_space': 'supplied_screenshot_pixels',
                     'native_psp_scale': 2 if (width, height) == (960, 544) else None,
                     'regions': [{'id': key, 'rect': rect} for key, rect in regions]})
    report = {'schema_version': 1, 'screenshots': rows,
              'measurement_status': 'Manual bounded inspection regions; not final glyph masks or renderer limits.',
              'dynamic_name_limit': 'Not established. Confirmation is a cropped screenshot; its full-screen placement is unknown.',
              'related_targets': ['work/translation/en/setup_ui.screenshot_drafts.json',
                                  'work/translation/en/setup_ui.related_drafts.json']}
    print(json.dumps({'mode': 'write' if args.write else 'dry run', 'destination': str(destination),
                      'files': rows}, indent=2))
    if args.write:
        destination.mkdir()
        for row in rows:
            target = destination / row['image_file']
            shutil.copyfile(row['source_path'], target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Screenshot copy changed bytes')
        (destination / 'index.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
