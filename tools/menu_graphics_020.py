"""Prepare native 0.1.20 Summon Index controls without writing a release image."""
import hashlib
from pathlib import Path

from PIL import Image

from sn3_archive import ROOT
from sn3_ui_textures import texture_records, decode_texture
from setup_ui_patch import encode_texture
from menu_art_015 import descend, replace_tree


ART = ROOT / 'work/ui/menu_0.1.20'
GENERATED = ART / 'summon_controls_generated.png'
PACKS = (2952, 2953, 2954, 2955)
TARGETS = (11, 12, 13, 14, 15, 16)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _artwork():
    """Crop the six generated controls in their source layout to native geometry."""
    sheet = Image.open(GENERATED).convert('RGBA')
    assert sheet.size == (1512, 1040)
    # The first four controls have transparent surrounds.  The lower diagram is
    # a single 256x80 native panel split by the original texture table into
    # sprites 15 (top 64 rows) and 16 (the 16-row continuation).
    crops = {
        11: (28, 18, 305, 118),
        12: (28, 160, 305, 261),
        13: (22, 304, 389, 404),
        14: (22, 442, 395, 546),
    }
    native = {}
    for number, box in crops.items():
        size = (64, 24) if number in (11, 12) else (72, 24)
        native[number] = sheet.crop(box).resize(size, Image.Resampling.LANCZOS)
    panel = sheet.crop((0, 560, 1512, 1040)).resize((256, 80), Image.Resampling.LANCZOS)
    native[15] = panel.crop((0, 0, 256, 64))
    native[16] = panel.crop((0, 64, 256, 80))
    return native


def prepare(source):
    """Return patched 02.DAT resources and a no-write verification report."""
    art = _artwork()
    resources, report = {}, {'version': '0.1.20', 'scope': 'Summon Index native controls only', 'packs': []}
    for pack in PACKS:
        original = source.resource('02.DAT', pack)
        target = descend(original, [2])
        records = texture_records(target)
        assert {n for n in TARGETS} <= {r['number'] for r in records}
        changed = target
        rows = []
        for number in TARGETS:
            row = records[number]
            before = decode_texture(changed, row)
            after, decoded, changed_pixels = encode_texture(changed, row, art[number])
            # The encoder guarantees nonchanged pixels inside the texture.  This
            # loop independently proves every other texture in the pack is exact.
            for other in records:
                if other['number'] != number:
                    assert decode_texture(after, other).tobytes() == decode_texture(changed, other).tobytes()
            assert decoded.size == before.size
            changed = after
            rows.append({'sprite': number, 'size': list(decoded.size), 'changed_pixels': changed_pixels,
                         'rgba_sha256': sha(decoded.tobytes())})
        result = replace_tree(original, {(2,): changed})
        assert len(result) == len(original)
        resources[f'02:{pack:05d}'] = result
        report['packs'].append({'resource_id': f'02:{pack:05d}', 'source_sha256': sha(original),
                                'output_sha256': sha(result), 'sprites': rows,
                                'outside_target_sprites_unchanged': True})
    report['generated_art_sha256'] = sha(GENERATED.read_bytes())
    report['sprite16_continuation'] = {
        'source': 'lower 16 rows of the generated 256x80 downsampled diagram',
        'grid_continues': True,
        'note': 'The generated lower panel preserves the table/grid through the sprite-16 boundary; sprite 16 is not blank.'
    }
    return resources, report


def write_preview(source, path=None):
    """Render the six decoded native sprites as a review-only contact image."""
    resources, report = prepare(source)
    data = descend(resources['02:02952'], [2]); records = texture_records(data)
    images = [decode_texture(data, records[n]) for n in TARGETS]
    canvas = Image.new('RGBA', (256, 24 * 4 + 80), (0, 0, 0, 0))
    for index, image in enumerate(images[:4]): canvas.paste(image, (0, index * 24))
    canvas.paste(images[4], (0, 96)); canvas.paste(images[5], (0, 160))
    out = Path(path) if path else ART / 'summon_controls_native_preview.png'
    canvas.save(out)
    return out, report
