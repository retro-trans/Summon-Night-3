"""Build a pixel-only Options mask correction on immutable 0.1.77."""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from sn3_archive import ROOT, GameSource
from build_candidate import hash_file
from build_battle_077 import verify_inputs
from build_battle import clean
from options_art_078 import prepare


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    base = ROOT / 'work/output/0.1.77'
    dest = ROOT / 'work/output/0.1.78'
    previous = json.loads((base / 'manifest.json').read_text(encoding='utf8'))
    prior = base / previous['output_iso']
    assert hash_file(prior) == previous['output_sha256']
    verify_inputs(previous['inputs_sha256'])
    with GameSource(prior) as source:
        replacement, report = prepare(source, a.write)
        row = source.indexes['02.DAT']['entries'][33]
        offset = source.files['02.DAT']['sector'] * 2048 + row['offset']
        assert len(replacement) == row['size']
    print(json.dumps(dict(mode='write' if a.write else 'preview', version='0.1.78',
        destination=str(dest), corrected_sprites=[13, 15], iso_layout_unchanged=True), indent=2), flush=True)
    if not a.write:
        return
    assert not dest.exists()
    dest.mkdir()
    iso = dest / 'Summon_Night_3_EN_0.1.78.iso'
    shutil.copyfile(prior, iso)
    with iso.open('r+b') as f:
        f.seek(offset); f.write(replacement)
    assert iso.stat().st_size == prior.stat().st_size
    # Compare every byte outside the one fixed-size resource, not just files.
    with prior.open('rb') as before, iso.open('rb') as after:
        cursor = 0
        changed = 0
        while True:
            old = before.read(4 * 1024 * 1024); new = after.read(len(old))
            if not old:
                assert not after.read(1)
                break
            lo = max(0, offset - cursor); hi = min(len(old), offset + len(replacement) - cursor)
            if lo < hi:
                assert old[:lo] == new[:lo] and old[hi:] == new[hi:]
                changed += sum(x != y for x, y in zip(old[lo:hi], new[lo:hi]))
            else:
                assert old == new
            cursor += len(old)
    with GameSource(iso) as current:
        assert current.resource('02.DAT', 33) == replacement
    shutil.copyfile(base / 'EBOOT.elf', dest / 'EBOOT.elf')
    manifest = clean(copy.deepcopy(previous))
    inputs = dict(previous['inputs_sha256'])
    for name in ('build_options_078.py', 'options_art_078.py', 'options_runtime_078.py', 'launch_options_078.ps1'):
        path = ROOT / 'tools' / name
        inputs[path.relative_to(ROOT).as_posix()] = hash_file(path)
    digest = hash_file(iso)
    report.update(iso_sha256=digest, changed_iso_bytes=changed,
        all_bytes_outside_resource_unchanged=True, executable_unchanged=True)
    manifest.update(version='0.1.78', built_at_utc=datetime.now(timezone.utc).isoformat(),
        output_iso=iso.name, output_size_bytes=iso.stat().st_size, output_sha256=digest,
        previous_build_sha256=previous['output_sha256'], inputs_sha256=inputs,
        options078_fix=report, static_validation=dict(comparison_build='0.1.77',
        single_resource='02.DAT:33', changed_iso_bytes=changed, iso_layout_unchanged=True,
        all_other_bytes_unchanged=True, executable_unchanged=True, runtime_verified=False))
    (dest / 'asset-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    (dest / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(iso=str(iso), sha256=digest, changed_iso_bytes=changed)), flush=True)


if __name__ == '__main__':
    main()
