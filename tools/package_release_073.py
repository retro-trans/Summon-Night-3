"""Package the verified 0.1.73 ISO and its two authorized release routes."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.73'
EXPECTED = '79e60216dbd74b6bc1b5abe14806557b17d4544f3c6518a5f6ada6a73f3be685'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def preflight():
    folder = ROOT / 'work/output' / VERSION
    manifest = json.loads((folder / 'manifest.json').read_text())
    target = folder / manifest['output_iso']
    assert digest(target) == manifest['output_sha256'] == EXPECTED
    assert target.stat().st_size == manifest['output_size_bytes'] == 1686472704
    for name, wanted in manifest['inputs_sha256'].items():
        assert digest(ROOT / name) == wanted, 'Changed build input: ' + name
    reports = {}
    for name, key in [('stability-report.json', 'stability_validation'),
                      ('runtime-validation.json', 'runtime_validation'),
                      ('name-cache-validation.json', 'name_cache_validation')]:
        path = folder / name
        reports[name] = json.loads(path.read_text())
        assert reports[name]['passed'], name
        assert digest(path) == manifest[key]['sha256'], name
        if 'iso_sha256' in reports[name]:
            assert reports[name]['iso_sha256'] == EXPECTED, name
    audit = reports['stability-report.json']
    assert len(audit['checks']) == 15 and all(c['passed'] for c in audit['checks'])
    names = reports['name-cache-validation.json']
    total = sum(names[k] for k in ('native_setter_getter_cases', 'default_initialization_cases', 'saved_record_cases'))
    assert total == 1220 and names['valid_bindings_preserved'] and names['invalid_bindings_cleared']
    runtime = reports['runtime-validation.json']
    assert runtime['fresh_boot'] and runtime['audio_enabled'] and runtime['cpu_core'] == 'JIT'
    assert not any(runtime[k] for k in ('save_state_used', 'runtime_memory_edits', 'ignore_bad_memory_access'))
    assert all(runtime['checks'][k] for k in ('created_summon', 'naming_completed', 'equipped_summon', 'subsequent_unit_menu', 'no_bad_execution_address'))
    assert runtime['checks']['spell_used'] == 'Random Hit'
    for item in runtime['evidence']:
        assert digest(ROOT / item['capture']) == item['png_sha256'], item['capture']
    # Publish a summary and screenshot references, never raw private saved records.
    summary = dict(version=VERSION, iso_sha256=EXPECTED, passed=True,
        input_hashes_verified=len(manifest['inputs_sha256']), regression_groups=15,
        native_name_cases=total, emulator=runtime['emulator'], cpu_core='JIT',
        audio_enabled=True, fresh_boot=True, save_state_used=False,
        runtime_memory_edits=False, ignore_bad_memory_access=False,
        combination=runtime['combination'], gameplay=runtime['checks'],
        report_sha256={name: digest(folder / name) for name in reports},
        evidence=runtime['evidence'], limits=runtime['limits'])
    return target, summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--prepare-evidence', action='store_true')
    args = parser.parse_args()
    target, summary = preflight()
    if args.prepare_evidence:
        path = ROOT / 'work/ui/release_0.1.73/VALIDATION.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
    commit = subprocess.check_output(['git', '-c', 'safe.directory=' + ROOT.as_posix(), 'rev-parse', 'HEAD'], text=True).strip()
    config = dict(game_id='summon-night-3', game_name='Summon Night 3', platform='PSP',
                  version=VERSION, source_commit=commit, patches=[])
    sources = [('original', ROOT / 'work/source/original.iso', 'SN3-English-v0.1.73.xdelta'),
               ('0.1.65', ROOT / 'work/output/0.1.65/Summon_Night_3_EN_0.1.65.iso', 'SN3-English-v0.1.65-to-v0.1.73.xdelta')]
    for version, source, name in sources:
        config['patches'].append(dict(patch=name, edition='Japanese NPJH50380', language='en',
            source_version=version, source_format='iso', target_format='iso', source=str(source), target=str(target)))
    out = ROOT / 'work/output/release-v0.1.73'
    print(json.dumps(dict(mode='write' if args.write else 'preview', preflight=summary['passed'],
        input_hashes=summary['input_hashes_verified'], destination=str(out), source_commit=commit,
        patches=[p['patch'] for p in config['patches']]), indent=2), flush=True)
    if not args.write:
        return
    sys.path.insert(0, str(ROOT / 'work/scratch/retro-trans-tools-release041'))
    from retro_trans.release import build_release, validate_directory
    config_path = ROOT / 'work/scratch/release073-config.json'
    config_path.write_text(json.dumps(config, indent=2), encoding='utf8')
    build_release(config_path, out, cache=ROOT / 'work/scratch/release041-cache')
    validate_directory(out)
    print('Both patches passed complete decoded-image hash verification.', flush=True)

if __name__ == '__main__':
    main()
