"""Package the validated 077-to-080 related UI test upgrade."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    a = p.parse_args()
    sys.path.insert(0, str(ROOT / 'work/scratch/retro-trans-tools-release073'))
    from retro_trans.core import sha256_file
    from retro_trans.release import build_release, validate_directory
    target = ROOT / 'work/output/0.1.81/Summon_Night_3_EN_0.1.81.iso'
    source = ROOT / 'work/output/0.1.77/Summon_Night_3_EN_0.1.77.iso'
    m = json.loads((target.parent / 'manifest.json').read_text(encoding='utf8'))
    assert sha256_file(target) == m['output_sha256']
    assert sha256_file(source) == json.loads((source.parent/'manifest.json').read_text())['output_sha256']
    for n in ('asset-validation.json', 'runtime-validation.json'):
        r = json.loads((target.parent / n).read_text(encoding='utf8'))
        assert r['passed'] and r['iso_sha256'] == m['output_sha256']
    config = dict(game_id='summon-night-3', game_name='Summon Night 3', platform='PSP', version='0.1.81',
        source_commit=subprocess.check_output(['git', '-c', 'safe.directory=' + ROOT.as_posix(), 'rev-parse', 'HEAD'], text=True).strip(),
        patches=[dict(patch='SN3-English-v0.1.77-to-v0.1.81.xdelta', edition='Japanese NPJH50380', language='en',
            source_version='0.1.77', source_format='iso', target_format='iso', source=str(source), target=str(target))])
    dest = ROOT / 'work/output/summon-test-v0.1.81'
    print(json.dumps(dict(mode='write' if a.write else 'preview', destination=str(dest)), indent=2), flush=True)
    if not a.write:
        return
    for path, wanted in m['inputs_sha256'].items():
        assert sha256_file(ROOT / path) == wanted, path
    path = ROOT / 'work/scratch/ui081-test-config.json'
    path.write_text(json.dumps(config, indent=2), encoding='utf8')
    build_release(path, dest, cache=ROOT / 'work/scratch/release073-cache')
    for name, original in {
        'README-v0.1.81.txt': ROOT / 'docs/UI_0.1.81.md',
        'CHANGELOG-v0.1.81.txt': ROOT / 'CHANGELOG.md',
        'GAMEPLAY-VALIDATION-v0.1.81.json': target.parent / 'runtime-validation.json',
        'ASSET-VALIDATION-v0.1.81.json': target.parent / 'asset-validation.json',
    }.items():
        (dest / name).write_bytes(original.read_bytes())
    files = sorted(p for p in dest.iterdir() if p.is_file() and p.name != 'SHA256SUMS.txt')
    (dest / 'SHA256SUMS.txt').write_text(''.join(sha256_file(p) + '  ' + p.name + '\n' for p in files), encoding='utf8')
    validate_directory(dest)
    archive = ROOT / 'work/output/SN3-English-test-v0.1.81.zip'
    assert not archive.exists()
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(dest.iterdir()):
            z.write(p, p.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {p.name for p in dest.iterdir()}
    print(json.dumps(dict(archive=str(archive), bytes=archive.stat().st_size,
        sha256=sha256_file(archive), full_decoded_image_verified=True)), flush=True)


if __name__ == '__main__':
    main()

