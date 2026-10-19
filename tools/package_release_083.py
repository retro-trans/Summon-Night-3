"""Package the validated 0.1.83 ISO with only the two published release routes."""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.83'
EXPECTED = '6cac982807c5cb6672fbbb74e166f973352ac7d30375fe4ccfee48d41babb5e6'
SOURCES = [
    ('original', 'work/source/original.iso', 'SN3-English-v0.1.83.xdelta',
     '00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda'),
    ('0.1.81', 'work/output/0.1.81/Summon_Night_3_EN_0.1.81.iso',
     'SN3-English-v0.1.81-to-v0.1.83.xdelta',
     '1e574f8ec2ed2917a2ee90b7c75427a6acb2ecca64727ca1215a3c683f2f89a8'),
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
    assert target.stat().st_size == manifest['output_size_bytes'] == 1696403456
    for name, wanted in manifest['inputs_sha256'].items():
        assert digest(ROOT / name) == wanted, 'Changed build input: ' + name
    assert len(manifest['inputs_sha256']) == 3358
    reports = {}
    report_hashes = {}
    for name in ('asset-validation.json', 'runtime-validation.json'):
        path = folder / name
        report_hashes[name] = digest(path)
        reports[name] = json.loads(path.read_text(encoding='utf8'))
        assert reports[name]['passed'] and reports[name]['iso_sha256'] == EXPECTED, name
    asset = reports['asset-validation.json']
    assert asset['native_binder_cases'] == 56 and asset['load_bases'] == 2
    assert asset['prior_bad_store_reproduced'] == '0x2c961c20'
    assert asset['adjacent_row_guards'] and asset['code_and_relocations_unchanged']
    assert asset['executable_matches_expected'] and asset['all_other_iso_files_unchanged']
    runtime = reports['runtime-validation.json']
    assert runtime['fresh_boot_normal_suspend'] and runtime['original_crash_reproduced']
    assert runtime['all_27_fresh_loaded_literals_verified'] and runtime['audio_enabled']
    assert runtime['emulator_instances'] == 1 and runtime['emulator_closed']
    assert not runtime['live_game_memory_writes'] and runtime['breakpoints_removed']
    assert runtime['original_supplied_state_repaired_for_replay']
    assert runtime['recovery']['code_unchanged'] and runtime['recovery']['combat_and_save_data_unchanged']
    assert len(runtime['screenshots']) == 4
    for item in runtime['screenshots']:
        assert item['visual_review_passed'] and digest(ROOT / item['path']) == item['sha256']
    inherited = []
    for version in ('0.1.82',):
        prior = ROOT / 'work/output' / version
        prior_manifest = json.loads((prior / 'manifest.json').read_text(encoding='utf8'))
        evidence = []
        for name in ('asset-validation.json', 'runtime-validation.json'):
            path = prior / name
            report = json.loads(path.read_text(encoding='utf8'))
            assert report['passed'] and report['iso_sha256'] == prior_manifest['output_sha256']
            evidence.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=digest(path)))
        inherited.append(dict(version=version, iso_sha256=prior_manifest['output_sha256'],
            reports=evidence, scope='Checks on the earlier local build; not a new full replay on 0.1.83.'))
    for _, path, _, wanted in SOURCES:
        assert digest(ROOT / path) == wanted, path
    summary = dict(version=VERSION, iso_sha256=EXPECTED, iso_bytes=target.stat().st_size,
        passed=True, input_hashes_verified=3358, encoder_source_window_bytes=268435456,
        asset_checks=asset, runtime=runtime, report_sha256=report_hashes,
        inherited_local_build_checks=inherited, limits=runtime['limitations'])
    return target, summary


def optimized_encode(engine, source, target, destination, cancel=None, progress=None):
    # The release builder still decodes and hashes each complete result. Reuse
    # the immutable test upgrade only after validating its manifest and assets.
    if destination.name == 'SN3-English-v0.1.81-to-v0.1.83.xdelta':
        from retro_trans.release import validate_directory
        previous = ROOT / 'work/output/summon-test-v0.1.83'
        manifest = validate_directory(previous)
        row, = manifest['patches']
        assert row['source_sha256'] == digest(source)
        assert row['target_sha256'] == digest(target) == EXPECTED
        shutil.copyfile(previous / destination.name, destination)
    else:
        env = os.environ.copy()
        env.pop('XDELTA', None)
        print('Encoding full patch with 256 MiB source window.', flush=True)
        subprocess.run([str(engine), '-e', '-D', '-A', '-B', '268435456', '-s',
            str(source), str(target), str(destination)], check=True, env=env,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        assert destination.stat().st_size < 30000000, 'Unexpectedly large full patch; investigate before publication.'
    print('Decoding and verifying ' + destination.name, flush=True)


def complete_assets(out, summary, validate_directory):
    extras = {
        'README-v0.1.83.txt': (ROOT / 'docs/RELEASE_0.1.83.md').read_bytes(),
        'CHANGELOG-v0.1.83.txt': (ROOT / 'CHANGELOG.md').read_bytes(),
        'GAMEPLAY-VALIDATION-v0.1.83.json': (json.dumps(summary, indent=2) + '\n').encode(),
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
        (out / (algorithm.upper() + 'SUMS-v0.1.83.txt')).write_text(lines, encoding='utf8')
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
        path = ROOT / 'work/ui/release_0.1.83/VALIDATION.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
    git = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
    commit = subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip()
    out = ROOT / 'work/output/release-v0.1.83'
    config = dict(game_id='summon-night-3', game_name='Summon Night 3', platform='PSP',
                  version=VERSION, source_commit=commit, patches=[])
    for version, source, patch, _ in SOURCES:
        config['patches'].append(dict(patch=patch, edition='Japanese NPJH50380', language='en',
            source_version=version, source_format='iso', target_format='iso',
            source=str(ROOT / source), target=str(target)))
    print(json.dumps(dict(mode='write' if args.write else 'preview', preflight=True,
        input_hashes=3358, destination=str(out), source_commit=commit,
        patches=[p['patch'] for p in config['patches']]), indent=2), flush=True)
    if not args.write:
        return
    assert not subprocess.check_output(git + ['status', '--porcelain', '-uno'], text=True).strip(), 'Commit tracked release changes first.'
    sys.path.insert(0, str(ROOT / 'work/scratch/retro-trans-tools-release073'))
    import retro_trans.release as release
    from retro_trans.release import build_release, validate_directory
    release.encode = optimized_encode
    config_path = ROOT / 'work/scratch/release083-config.json'
    config_path.write_text(json.dumps(config, indent=2), encoding='utf8')
    build_release(config_path, out, cache=ROOT / 'work/scratch/release073-cache')
    complete_assets(out, summary, validate_directory)
    print('Both complete decoded images, manifests and all release checksums verified.', flush=True)


if __name__ == '__main__':
    main()
