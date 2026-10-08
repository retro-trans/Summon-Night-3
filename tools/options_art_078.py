"""Repair selected Options text masks without changing native geometry or palettes."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from sn3_archive import ROOT
from menu_art_075 import descend, replace_tree, unpack
from sn3_ui_textures import texture_records, decode_texture
from setup_ui_patch import encode_texture

FOLDER = ROOT / 'work/ui/options_0.1.78'
TARGETS = (13, 14, 15)
LABELS = [(3, 4, 'Music Volume'), (6, None, 'Event Voices'), (7, None, 'Forecast'),
          (8, None, 'Cursor Direction'), (9, None, 'L/R Function'),
          (10, None, 'Music Volume selected'), (11, None, 'Event Voices selected'),
          (12, None, 'Forecast selected'), (13, 14, 'Cursor Direction selected'),
          (15, None, 'L/R Function selected')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(source, write=False):
    root = source.resource('02.DAT', 33)
    original = descend(root, [2])
    rows = texture_records(original)
    data = original
    reports = []
    for number in TARGETS:
        row = rows[number]
        path = ROOT / f'work/ui/menus_0.1.76/generated/33_2_{number}.png'
        glyph = Image.open(path).convert('RGBA')
        before = decode_texture(data, row)
        assert glyph.size == before.size
        # This is text, so the English glyph owns its alpha mask. Do not restore
        # the Japanese glyph alpha as the old size-based button heuristic did.
        data, after, changed = encode_texture(data, row, glyph)
        wanted = np.asarray(glyph)[:, :, 3]
        alpha = np.asarray(after)[:, :, 3]
        assert not np.any(alpha[wanted == 0]), 'Opaque pixels outside English glyph'
        if np.any(wanted > 200):
            assert np.any(alpha[wanted > 200]), 'English glyph disappeared'
        reports.append(dict(sprite=number, generated_path=str(path.relative_to(ROOT)).replace('\\', '/'),
            generated_sha256=sha(path.read_bytes()), native_size=list(before.size), changed_pixels=changed,
            unwanted_opaque_before=int(np.count_nonzero(np.asarray(before)[:, :, 3][wanted == 0])),
            unwanted_opaque_after=int(np.count_nonzero(alpha[wanted == 0])),
            before_sha256=sha(before.tobytes()), after_sha256=sha(after.tobytes())))
        if write:
            FOLDER.mkdir(parents=True, exist_ok=True)
            before.save(FOLDER / f'before_{number}.png')
            after.save(FOLDER / f'after_{number}.png')
    assert len(data) == len(original) and texture_records(data) == rows
    allowed = set()
    for number in TARGETS:
        row = rows[number]
        allowed.update(range(row['data_offset'], row['data_offset'] + row['data_size']))
    assert all(i in allowed for i, (a, b) in enumerate(zip(original, data)) if a != b)
    for row in rows:
        if row['number'] not in TARGETS:
            assert decode_texture(original, row).tobytes() == decode_texture(data, row).tobytes()
    new_root = replace_tree(root, {(2,): data})
    old_raw, old_ix, old_key = unpack(root)
    new_raw, new_ix, new_key = unpack(new_root)
    assert old_key == new_key and old_ix == new_ix
    for entry in old_ix['entries']:
        if entry['id'] == 2:
            continue
        a, n = entry['offset'], entry['size']
        assert old_raw[a:a+n] == new_raw[a:a+n]
    # No resource relocation is needed for this pixel-only correction.
    assert len(new_root) <= len(root)
    new_root += bytes(len(root) - len(new_root))
    report = dict(version='0.1.78', passed=True, source_root_sha256=sha(root),
        output_root_sha256=sha(new_root), root_size=len(root), masks=reports,
        native_palette_geometry_codec_preserved=True, other_textures_unchanged=True,
        other_resource_children_unchanged=True, resource_layout_unchanged=True)
    if write:
        canvas = Image.new('RGBA', (750, 540), (232, 219, 180, 255))
        draw = ImageDraw.Draw(canvas)
        for y, (a, b, label) in enumerate(LABELS):
            for column, leaf in enumerate((original, data)):
                im = decode_texture(leaf, rows[a])
                if b is not None:
                    second = decode_texture(leaf, rows[b])
                    joined = Image.new('RGBA', (im.width + second.width, im.height))
                    joined.alpha_composite(im, (0, 0)); joined.alpha_composite(second, (im.width, 0))
                    im = joined
                draw.text((column * 375, y * 52), label, fill='black')
                canvas.alpha_composite(im.resize((im.width * 2, im.height * 2)), (column * 375, y * 52 + 16))
        canvas.convert('RGB').save(FOLDER / 'mask_comparison.png')
        (FOLDER / 'asset-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    return new_root, report
