"""Verify both 081 routes using the public Retro Trans catalog and downloads."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '1e574f8ec2ed2917a2ee90b7c75427a6acb2ecca64727ca1215a3c683f2f89a8'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/scratch/retro-trans-live081')
    args = parser.parse_args()
    print(json.dumps(dict(mode='verify' if args.execute else 'preview',
        routes=['original -> 0.1.81', '0.1.77 -> 0.1.81'], destination=str(args.out)),
        indent=2), flush=True)
    if not args.execute:
        return
    assert not args.out.exists(), 'Choose a fresh output directory.'
    args.out.mkdir(parents=True)
    patcher = ROOT / 'work/scratch/retro-trans-tools-release073'
    sys.path.insert(0, str(patcher))
    from retro_trans import __version__
    from retro_trans.catalog import Catalog, assert_immutable, refresh_catalog, recognize, apply_plan
    from retro_trans.core import sha256_file
    old = Catalog(json.loads((patcher / 'retro_trans/resources/catalog.json').read_text(encoding='utf8')))
    cache = args.out / 'cache'
    catalog = refresh_catalog(cache=cache)
    assert_immutable(old, catalog)
    records = [r for r in catalog.data['releases']
        if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.81']
    record, = records
    manifest = json.loads((ROOT / 'work/output/release-v0.1.81/BUILD-MANIFEST.json').read_text(encoding='utf8'))
    assert record['manifest'] == manifest
    assert {p['patch'] for p in manifest['patches']} == {
        'SN3-English-v0.1.81.xdelta', 'SN3-English-v0.1.77-to-v0.1.81.xdelta'}
    print('Public catalog and prior identities: PASS', flush=True)
    routes = []
    for version, source in [
        ('original', ROOT / 'work/source/original.iso'),
        ('0.1.77', ROOT / 'work/output/0.1.77/Summon_Night_3_EN_0.1.77.iso')]:
        node, = [n for n in recognize(source, catalog)
            if n.game_name == 'Summon Night 3' and n.version == version]
        plan = catalog.plan(node, 'Latest')
        assert len(plan.edges) == 1 and plan.target.version == '0.1.81'
        output = args.out / ('automatic-' + version + '.iso')
        result = apply_plan(source, output, plan, catalog, cache=cache)
        assert result.stat().st_size == 1695072256 and sha256_file(result) == EXPECTED
        assert any(n.version == '0.1.81' for n in recognize(result, catalog))
        routes.append(dict(source_version=version, patch=plan.edges[0].asset.name,
            public_download=True, automatic_patch=True, target_recognition=True,
            target_sha256=EXPECTED, target_bytes=result.stat().st_size))
        result.unlink()
        print('Public automatic route ' + version + ' -> 0.1.81: PASS', flush=True)
    report = dict(version='0.1.81', passed=True, retro_trans_version=__version__,
        patcher_commit=subprocess.check_output(['git', '-c', 'safe.directory=' + patcher.as_posix(),
            '-C', str(patcher), 'rev-parse', 'HEAD'], text=True).strip(),
        public_catalog_discovery=True, prior_cached_catalog_immutable=True,
        routes=routes, target_sha256=EXPECTED, target_bytes=1695072256,
        scope='Both public ISO/catalog/engine routes, fresh cache. No emulator, GUI or CHD test.')
    (args.out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    evidence = ROOT / 'work/ui/release_0.1.81/PUBLIC-VALIDATION.json'
    evidence.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
