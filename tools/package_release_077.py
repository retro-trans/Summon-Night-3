"""Package the validated 0.1.77 ISO with only the two published release routes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.77'
EXPECTED = 'd35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427'
SOURCES = [
    ('original', 'work/source/original.iso', 'SN3-English-v0.1.77.xdelta',
     '00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda'),
    ('0.1.73', 'work/output/0.1.73/Summon_Night_3_EN_0.1.73.iso',
     'SN3-English-v0.1.73-to-v0.1.77.xdelta',
     '79e60216dbd74b6bc1b5abe14806557b17d4544f3c6518a5f6ada6a73f3be685'),
]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def preflight():
    folder = ROOT / 'work/output' / VERSION
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf8'))
    target = folder / manifest['output_iso']
    assert digest(target) == manifest['output_sha256'] == EXPECTED
    assert target.stat().st_size == manifest['output_size_bytes'] == 1691269120
    for name, wanted in manifest['inputs_sha256'].items():
        assert digest(ROOT / name) == wanted, 'Changed build input: ' + name
    assert len(manifest['inputs_sha256']) == 3310
    reports = {}
    report_hashes = manifest['battle077_validation']['reports']
    for name in ('battle-validation.json', 'stability-report.json', 'runtime-validation.json'):
        path = folder / name
        assert digest(path) == report_hashes[name], name
        reports[name] = json.loads(path.read_text(encoding='utf8'))
        assert reports[name]['passed'] and reports[name]['iso_sha256'] == EXPECTED, name
    stability = reports['stability-report.json']
    assert len(stability['checks']) == 14 and all(c['passed'] for c in stability['checks'])
    battle = reports['battle-validation.json']
    assert len(battle['routing_cases']) == 16
    assert len(battle['crafting_messages']) == 4
    assert battle['skill_list_left_aligned'] and battle['animation_centering_preserved']
    assert battle['title_import']['translated_sprites'] == 29
    assert battle['title_import']['native_geometry_codec_palette_preserved']
    runtime = reports['runtime-validation.json']
    assert runtime['fresh_boot'] and runtime['normal_in_game_save'] and runtime['audio_enabled']
    assert runtime['single_emulator'] and not runtime['save_state_used']
    assert not runtime['runtime_memory_edits'] and all(runtime['checks'].values())
    assert len(runtime['screenshots']) == 8
    for item in runtime['screenshots']:
        assert item['verified_iso_sha256'] == EXPECTED
        assert digest(ROOT / item['path']) == item['sha256'], item['path']
    for _, path, _, wanted in SOURCES:
        assert digest(ROOT / path) == wanted, path
    summary = dict(version=VERSION, iso_sha256=EXPECTED, iso_bytes=target.stat().st_size,
        passed=True, input_hashes_verified=3310, regression_groups=14,
        native_routing_cases=16, native_title_imports=29, crafting_message_groups=4,
        emulator=runtime['emulator'], fresh_boot=True, normal_in_game_save=True,
        audio_enabled=True, single_emulator=True, save_state_used=False,
        runtime_memory_edits=False, gameplay=runtime['checks'], spell_cast_tested=False,
        report_sha256=report_hashes, screenshots=runtime['screenshots'],
        limits=runtime['limits'])
    return target, summary


def complete_assets(out, summary, validate_directory):
    extras = {
        'README-v0.1.77.txt': (ROOT / 'docs/RELEASE_0.1.77.md').read_bytes(),
        'CHANGELOG-v0.1.77.txt': (ROOT / 'CHANGELOG.md').read_bytes(),
        'GAMEPLAY-VALIDATION-v0.1.77.json': (json.dumps(summary, indent=2) + '\n').encode(),
    }
    for name, data in extras.items():
        path = out / name
        assert not path.exists(), name
        path.write_bytes(data)
    # The public catalog fetches only its four core files before validation.
    # Keep generic sums limited to those files; versioned sums cover the extras.
    core = sorted({s[2] for s in SOURCES} | {'BUILD-MANIFEST.json', 'VALIDATION.json'})
    (out / 'SHA256SUMS.txt').write_text(''.join(digest(out / n) + '  ' + n + '\n' for n in core), encoding='utf8')
    payload = sorted(p for p in out.iterdir() if p.is_file())
    for algorithm in ('sha1', 'sha256'):
        lines = ''.join(hashlib.new(algorithm, p.read_bytes()).hexdigest() + '  ' + p.name + '\n'
                        for p in payload)
        (out / (algorithm.upper() + 'SUMS-v0.1.77.txt')).write_text(lines, encoding='utf8')
    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != 'SHA256SUMS.txt')
    assert {p.name for p in out.glob('*.xdelta')} == {s[2] for s in SOURCES}
    assert len(files) + 1 == 10 and all(p.suffix in ('.json', '.txt', '.xdelta') for p in files)
    validate_directory(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--prepare-evidence', action='store_true')
    args = parser.parse_args()
    target, summary = preflight()
    if args.prepare_evidence:
        path = ROOT / 'work/ui/release_0.1.77/VALIDATION.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
    git = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
    commit = subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip()
    out = ROOT / 'work/output/release-v0.1.77'
    config = dict(game_id='summon-night-3', game_name='Summon Night 3', platform='PSP',
                  version=VERSION, source_commit=commit, patches=[])
    for version, source, patch, _ in SOURCES:
        config['patches'].append(dict(patch=patch, edition='Japanese NPJH50380', language='en',
            source_version=version, source_format='iso', target_format='iso',
            source=str(ROOT / source), target=str(target)))
    print(json.dumps(dict(mode='write' if args.write else 'preview', preflight=True,
        input_hashes=3310, destination=str(out), source_commit=commit,
        patches=[p['patch'] for p in config['patches']]), indent=2), flush=True)
    if not args.write:
        return
    assert not subprocess.check_output(git + ['status', '--porcelain', '-uno'], text=True).strip(), 'Commit tracked release changes first.'
    sys.path.insert(0, str(ROOT / 'work/scratch/retro-trans-tools-release073'))
    from retro_trans.release import build_release, validate_directory
    config_path = ROOT / 'work/scratch/release077-config.json'
    config_path.write_text(json.dumps(config, indent=2), encoding='utf8')
    build_release(config_path, out, cache=ROOT / 'work/scratch/release073-cache')
    complete_assets(out, summary, validate_directory)
    print('Both complete decoded images, manifests and all release checksums verified.', flush=True)


if __name__ == '__main__':
    main()
