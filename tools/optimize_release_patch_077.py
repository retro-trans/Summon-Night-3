"""Prepare a smaller 077 full patch and a catalog-preserving withdrawal record.

No GitHub writes. --write --reuse-verified stages the already audited candidate;
--write without reuse creates and fully decodes a new candidate first.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PATCHER = ROOT / 'work/scratch/retro-trans-tools-release073'
OLD_NAME = 'SN3-English-v0.1.77.xdelta'
NEW_NAME = 'SN3-English-v0.1.77-optimized.xdelta'
EXPECTED = 'd35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427'
WINDOW = 268435456


def digest(path, algorithm='sha256'):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--reuse-verified', action='store_true')
    args = parser.parse_args()
    candidate = ROOT / 'work/scratch/release077-optimized'
    previous = ROOT / 'work/output/release-v0.1.77'
    destination = ROOT / 'work/output/release-v0.1.77-optimized'
    source = ROOT / 'work/source/original.iso'
    target = ROOT / 'work/output/0.1.77/Summon_Night_3_EN_0.1.77.iso'
    print(json.dumps(dict(mode='write' if args.write else 'preview', destination=str(destination),
        old_patch=OLD_NAME, new_patch=NEW_NAME, source_window_bytes=WINDOW,
        iso_unchanged=True), indent=2), flush=True)
    if not args.write:
        return
    assert not destination.exists()
    assert digest(source) == '00b9fe052e7f516a2975cb3e625682640ec17edb7bd23f3a785f6c73d4bbefda'
    assert digest(target) == EXPECTED and target.stat().st_size == 1691269120
    sys.path.insert(0, str(PATCHER))
    from retro_trans.core import engine_context, decode
    from retro_trans.release import validate_directory
    from retro_trans.catalog import Catalog, assert_immutable
    if not args.reuse_verified:
        candidate.mkdir()
        started = time.monotonic()
        env = os.environ.copy()
        env.pop('XDELTA', None)
        with engine_context(cache=ROOT / 'work/scratch/release073-cache') as engine:
            subprocess.run([str(engine), '-e', '-D', '-A', '-B', str(WINDOW), '-s',
                str(source), str(target), str(candidate / NEW_NAME)], check=True, env=env,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            decoded = candidate / 'verification.iso'
            decode(engine, source, candidate / NEW_NAME, decoded, 1691269120)
            assert digest(decoded) == EXPECTED and decoded.stat().st_size == 1691269120
            report = dict(version='0.1.77', passed=True, encoder_source_window_bytes=WINDOW,
                original_patch_bytes=(previous / OLD_NAME).stat().st_size,
                optimized_patch_bytes=(candidate / NEW_NAME).stat().st_size,
                optimized_patch_sha256=digest(candidate / NEW_NAME), target_sha256=EXPECTED,
                target_bytes=decoded.stat().st_size, complete_decoded_image_verified=True,
                elapsed_seconds=round(time.monotonic() - started, 2))
            (candidate / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
            decoded.unlink()
    report = json.loads((candidate / 'validation.json').read_text(encoding='utf8'))
    assert report['passed'] and report['complete_decoded_image_verified']
    assert report['encoder_source_window_bytes'] == WINDOW and report['target_sha256'] == EXPECTED
    assert digest(candidate / NEW_NAME) == report['optimized_patch_sha256']
    assert (candidate / NEW_NAME).stat().st_size == report['optimized_patch_bytes'] < 20000000
    validate_directory(previous)
    old_manifest = json.loads((previous / 'BUILD-MANIFEST.json').read_text(encoding='utf8'))
    manifest = copy.deepcopy(old_manifest)
    changed = [p for p in manifest['patches'] if p['patch'] == OLD_NAME]
    assert len(changed) == 1 and changed[0]['source_version'] == 'original'
    changed[0].update(patch=NEW_NAME, patch_bytes=report['optimized_patch_bytes'],
                      patch_sha256=report['optimized_patch_sha256'])
    assert all(p['target_sha256'] == EXPECTED for p in manifest['patches'])
    old_validation = json.loads((previous / 'VALIDATION.json').read_text(encoding='utf8'))
    assert all(p['roundtrip_verified'] for p in old_validation['patches'])
    destination.mkdir()
    shutil.copyfile(candidate / NEW_NAME, destination / NEW_NAME)
    upgrade = 'SN3-English-v0.1.73-to-v0.1.77.xdelta'
    shutil.copyfile(previous / upgrade, destination / upgrade)
    (destination / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf8')
    validation = dict(schema_version=1, manifest_sha256=digest(destination / 'BUILD-MANIFEST.json'),
        patches=[dict(patch=p['patch'], roundtrip_verified=True, target_sha256=p['target_sha256'])
                 for p in manifest['patches']])
    (destination / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n', encoding='utf8')
    shutil.copyfile(ROOT / 'docs/RELEASE_0.1.77_REPACK.md', destination / 'README-v0.1.77.txt')
    shutil.copyfile(ROOT / 'CHANGELOG.md', destination / 'CHANGELOG-v0.1.77.txt')
    shutil.copyfile(previous / 'GAMEPLAY-VALIDATION-v0.1.77.json', destination / 'GAMEPLAY-VALIDATION-v0.1.77.json')
    core = sorted({p['patch'] for p in manifest['patches']} | {'BUILD-MANIFEST.json', 'VALIDATION.json'})
    (destination / 'SHA256SUMS.txt').write_text(''.join(digest(destination / n) + '  ' + n + '\n' for n in core), encoding='utf8')
    payload = sorted(destination.iterdir())
    for algorithm in ('sha1', 'sha256'):
        (destination / (algorithm.upper() + 'SUMS-v0.1.77.txt')).write_text(
            ''.join(digest(p, algorithm) + '  ' + p.name + '\n' for p in payload), encoding='utf8')
    validate_directory(destination)
    # Preserve the original patch URL/hash as a withdrawn edge. Never overwrite
    # a cataloged patch URL with a new binary or discard a cached identity.
    path = PATCHER / 'retro_trans/resources/catalog.json'
    old_catalog = json.loads(path.read_text(encoding='utf8'))
    catalog = copy.deepcopy(old_catalog)
    record = next(r for r in catalog['releases'] if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.77')
    assert record['manifest'] == old_manifest
    retired = copy.deepcopy(record)
    retired['manifest']['patches'] = [p for p in retired['manifest']['patches'] if p['patch'] == OLD_NAME]
    retired['assets'] = {OLD_NAME: retired['assets'][OLD_NAME]}
    retired['reason'] = 'Oversized full patch withdrawn after encoding optimization; replacement recreates the identical 0.1.77 ISO.'
    assert not any(r['repo'] == retired['repo'] and r['tag'] == retired['tag'] for r in catalog.get('withdrawn_releases', []))
    catalog.setdefault('withdrawn_releases', []).append(retired)
    record['manifest'] = manifest
    old_url = record['assets'].pop(OLD_NAME)
    record['assets'][NEW_NAME] = old_url.removesuffix(OLD_NAME) + NEW_NAME
    assert_immutable(Catalog(old_catalog), Catalog(catalog))
    (candidate / 'catalog-before.json').write_bytes((json.dumps(old_catalog, indent=2) + '\n').encode('utf8'))
    (candidate / 'catalog-after.json').write_bytes((json.dumps(catalog, indent=2) + '\n').encode('utf8'))
    evidence = ROOT / 'work/ui/release_0.1.77/OPTIMIZATION-VALIDATION.json'
    evidence.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(staged=True, patch_bytes=report['optimized_patch_bytes'],
        decoded_iso_verified=True, upgrade_unchanged=True, catalog_immutability_passed=True,
        retired_patch=OLD_NAME, published_patch=NEW_NAME), indent=2), flush=True)


if __name__ == '__main__':
    main()
