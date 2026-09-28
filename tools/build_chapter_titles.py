"""Import reviewed imagegen title cards and build 0.1.8; dry run precedes writes."""
import argparse, copy, json, shutil
from datetime import datetime, timezone
from PIL import Image, ImageDraw
from build_candidate import *
from setup_ui_patch import encode_texture
from sn3_ui_textures import texture_records, decode_texture

ASSETS = ROOT / 'work/ui/chapter_0.1.8'
BASE = ROOT / 'work/output/0.1.7'
DEST = ROOT / 'work/output/0.1.8'
DRAFT = ROOT / 'work/translation/en/chapter_titles.draft.json'
REVIEW = ROOT / 'work/translation/en/chapter_titles.meaning_review.json'
TARGET = ROOT / 'work/translation/en/chapter_titles.targets.json'


def prepare_art():
    spec = json.loads((ASSETS / 'prompts.json').read_text(encoding='utf-8'))
    draft = json.loads(DRAFT.read_text(encoding='utf-8'))
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    assert review['draft_sha256'] == hash_file(DRAFT)
    assert review['reviewed_rows'] == 30 and review['status'] == 'pass_with_nonblocking_uncertainties'
    assets = {a['pack']: a for a in spec['assets']}
    assert set(assets) == set(range(93, 123))
    targets = copy.deepcopy(draft)
    targets['status'] = 'meaning_reviewed'
    targets['inputs_sha256'] = {str(p.relative_to(ROOT)).replace('\\', '/'): hash_file(p) for p in (DRAFT, REVIEW)}
    targets['glossary_normalization'] = 'No newly translated names require normalization; native English subtitles retained verbatim.'
    for e in targets['entries']:
        a = assets[e['pack']]
        assert (e['title'], e['heading'], e['subtitle']) == (a['title'], a['heading'], a['subtitle'])
        e['meaning_status'] = 'meaning_reviewed'
        e['subtitle_policy'] = 'Native English wording, case and punctuation verified; preserved.'
        e['generated_image'] = f"work/ui/chapter_0.1.8/{a['id']}_generated.png"
    packs, renders, records = {}, [], []
    with GameSource() as source:
        for n in range(92, 123):
            a = assets[94 if n == 92 else n]
            local = ASSETS / (a['id'] + '_generated.png')
            image_path = local if local.exists() else Path(a['source'])
            generated = Image.open(image_path)
            assert generated.mode == 'RGBA', (n, generated.mode)
            alpha = generated.getchannel('A')
            assert alpha.getextrema() == (0, 255), n
            assert alpha.getpixel((0, 0)) == 0 and alpha.getpixel((generated.width - 1, generated.height - 1)) == 0
            assert abs(generated.width / generated.height - 480 / 272) < .02
            packed_original = source.resource('02.DAT', n)
            data, used = decompress(packed_original, 0x9831)
            assert not any(packed_original[used:])
            index = parse_index(data, len(data))
            assert len(index['entries']) == 2
            original = child(data, index, 0)
            audio = child(data, index, 1)
            assert audio.startswith(b'RIFF')
            rows = list(texture_records(original))
            assert len(rows) == 1
            row = rows[0]
            before = decode_texture(original, row)
            assert before.size == (480, 272)
            # Mechanical full-canvas downsample only: never crop/repaint lettering.
            fitted = generated.resize(before.size, Image.Resampling.LANCZOS)
            out, decoded, pixels = encode_texture(original, row, fitted)
            assert texture_records(out) == texture_records(original)
            start, size = row['data_offset'], row['data_size']
            assert out[:start] == original[:start] and out[start + size:] == original[start + size:]
            assert decoded.getchannel('A').getpixel((0, 0)) == 0
            modified = repack(data, {0: out})
            packed = compress(modified, 0x9831)
            assert decompress(packed, 0x9831)[0] == modified
            new_index = parse_index(modified, len(modified))
            assert child(modified, new_index, 1) == audio
            assert len(modified) == len(data)
            name = f'02_{n:05d}_00000_sprite_000.png'
            renders.append((name, decoded))
            packs[n] = packed
            records.append(dict(pack=n, asset_id=a['id'], title=a['title'], native_image=name,
                generated_sha256=hash_file(image_path), generated_size=generated.size,
                native_size=decoded.size, modified_pixels=pixels,
                audio_sha256=hashlib.sha256(audio).hexdigest(), audio_unchanged=True,
                original_decoded_bytes=len(data), modified_decoded_bytes=len(modified),
                native_rgba_sha256=hashlib.sha256(decoded.tobytes()).hexdigest(),
                packed_sha256=hashlib.sha256(packed).hexdigest()))
            print(f"Validated {n}: {a['title']} ({len(packed)} packed bytes)", flush=True)
    art = dict(version='0.1.8', method='built-in image_gen', distinct_titles=30, native_cards=31,
        records=records, imports='Full-canvas downsample to 480x272 and original-palette quantization. No drawn overlays.',
        inputs_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): hash_file(p) for p in
            (DRAFT, REVIEW, ASSETS / 'prompts.json', Path(__file__))})
    return packs, renders, art, targets


def write_assets(packs, renders, art, targets):
    assert not (ASSETS / 'index.json').exists()
    spec = json.loads((ASSETS / 'prompts.json').read_text(encoding='utf-8'))
    for a in spec['assets']:
        shutil.copyfile(a['source'], ASSETS / (a['id'] + '_generated.png'))
    for name, im in renders:
        im.save(ASSETS / name)
    for n, data in packs.items():
        (ASSETS / f'pack_{n:05d}.bin').write_bytes(data)
    # Contact sheets contain native decoded pixels, not pre-quantization previews.
    for batch in range(4):
        selected = renders[batch * 8:(batch + 1) * 8]
        sheet = Image.new('RGB', (960, 296 * ((len(selected) + 1) // 2)), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        for i, (name, im) in enumerate(selected):
            x, y = (i % 2) * 480, (i // 2) * 296
            draw.text((x + 8, y + 4), name, fill='white')
            sheet.paste(im, (x, y + 24), im)
        sheet.save(ASSETS / f'contact_{batch:02d}.png')
    (ASSETS / 'index.json').write_text(json.dumps(art, indent=2) + '\n', encoding='utf-8')
    TARGET.write_text(json.dumps(targets, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-assets', action='store_true')
    parser.add_argument('--write-iso', action='store_true')
    args = parser.parse_args()
    assert not (args.write_assets and args.write_iso)
    packs, renders, art, targets = prepare_art()
    print(json.dumps(dict(mode='write assets' if args.write_assets else 'write ISO' if args.write_iso else 'dry run',
        destination=str(DEST), cards=art['native_cards'], sample=art['records'][1]), indent=2), flush=True)
    if args.write_assets:
        write_assets(packs, renders, art, targets)
        return
    if not args.write_iso:
        return
    assert json.loads((ASSETS / 'index.json').read_text(encoding='utf-8')) == json.loads(json.dumps(art))
    assert json.loads(TARGET.read_text(encoding='utf-8')) == targets
    assert not DEST.exists()
    previous = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8'))
    assert hash_file(BASE / previous['output_iso']) == previous['output_sha256']
    executable = (BASE / 'EBOOT.elf').read_bytes()
    assert hashlib.sha256(executable).hexdigest() == previous['executable_patch']['patched_elf_sha256']
    with GameSource() as source, GameSource(BASE / previous['output_iso']) as prior:
        plans, changes, entries = prepare(source)
        scripts, reports = prepare_scripts(source, ROOT / 'work/translation/en/opening_harbor_0.1.5.targets.json', FONT_PROFILE)
        assert reports[0]['decoded_sha256'] == previous['script_changes'][0]['decoded_sha256']
        allpacks = {n: prior.resource('02.DAT', n) for n in (28, 29, 30, 31, 32)}
        allpacks.update(packs)
        plan02 = plan_bank(source, '02.DAT', allpacks)
        combined = dict(plans[0]['replacements'])
        combined.update(scripts)
        combined[44] = repack(combined[44], {1: plan02['index_bytes']})
        plans[0] = plan_bank(source, '00.DAT', combined)
        plans.append(plan02)
        assert hash_file(ROOT / 'work/source/original.iso') == previous['source_iso_sha256']
        DEST.mkdir()
        iso = DEST / 'Summon_Night_3_EN_0.1.8.iso'
        partial = iso.with_suffix('.iso.partial')
        files = {'/PSP_GAME/SYSDIR/EBOOT.BIN': executable}
        write_iso(source, plans, partial, files)
        validation = verify_candidate(partial, source, changes, entries, reports, files, {'02.DAT': allpacks})
        partial.rename(iso)
        manifest = copy.deepcopy(previous)
        for k in ('runtime_validation', 'setup_ui_runtime_verified'):
            manifest.pop(k, None)
        manifest.update(version='0.1.8', built_at_utc=datetime.now(timezone.utc).isoformat(),
            output_iso=iso.name, output_size_bytes=iso.stat().st_size, output_sha256=hash_file(iso),
            static_validation=validation, script_changes=reports, chapter_titles=art,
            previous_build_sha256=previous['output_sha256'])
        for p in [Path(__file__), DRAFT, REVIEW, TARGET, ASSETS / 'prompts.json', ASSETS / 'index.json']:
            manifest['inputs_sha256'][str(p.relative_to(ROOT)).replace('\\', '/')] = hash_file(p)
        for a in json.loads((ASSETS / 'prompts.json').read_text(encoding='utf-8'))['assets']:
            p = ASSETS / (a['id'] + '_generated.png')
            manifest['inputs_sha256'][str(p.relative_to(ROOT)).replace('\\', '/')] = hash_file(p)
        (DEST / 'EBOOT.elf').write_bytes(executable)
        (DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(built=str(iso), sha256=manifest['output_sha256'], validation=validation), indent=2))


if __name__ == '__main__':
    main()
