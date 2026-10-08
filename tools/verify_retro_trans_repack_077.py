"""Verify both public 077 routes and the retired oversized patch identity."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'd35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/scratch/release077-repack-live')
    args = parser.parse_args()
    print(json.dumps(dict(mode='verify' if args.execute else 'preview', destination=str(args.out),
        routes=['original -> 0.1.77', '0.1.73 -> 0.1.77'],
        new_full_patch='SN3-English-v0.1.77-optimized.xdelta'), indent=2), flush=True)
    if not args.execute:
        return
    assert not args.out.exists()
    args.out.mkdir(parents=True)
    patcher = ROOT / 'work/scratch/retro-trans-tools-release073'
    sys.path.insert(0, str(patcher))
    from retro_trans import __version__
    from retro_trans.catalog import Catalog, assert_immutable, refresh_catalog, recognize, apply_plan
    from retro_trans.core import sha256_file
    cache = args.out / 'cache'
    catalog = refresh_catalog(cache=cache)
    old = json.loads((ROOT / 'work/scratch/release077-optimized/catalog-before.json').read_text(encoding='utf8'))
    assert_immutable(Catalog(old), catalog)
    records = [r for r in catalog.data['releases'] if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.77']
    assert len(records) == 1
    patches = {p['patch']: p for p in records[0]['manifest']['patches']}
    assert set(patches) == {'SN3-English-v0.1.77-optimized.xdelta', 'SN3-English-v0.1.73-to-v0.1.77.xdelta'}
    assert patches['SN3-English-v0.1.77-optimized.xdelta']['patch_bytes'] == 14383778
    retired = [r for r in catalog.data['withdrawn_releases'] if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.77']
    assert len(retired) == 1 and len(retired[0]['manifest']['patches']) == 1
    p = retired[0]['manifest']['patches'][0]
    assert p['patch'] == 'SN3-English-v0.1.77.xdelta' and p['patch_bytes'] == 407197655
    assert p['patch_sha256'] == 'bd58e1a0b196464f0c586c8d68cea4ad21ac08677cadac64490ba6e8c794d08c'
    print('Public catalog and cached identity preservation: PASS', flush=True)
    routes = []
    for version, source in [
        ('original', ROOT / 'work/source/original.iso'),
        ('0.1.73', ROOT / 'work/output/0.1.73/Summon_Night_3_EN_0.1.73.iso')]:
        nodes = [n for n in recognize(source, catalog) if n.game_name == 'Summon Night 3' and n.version == version]
        assert len(nodes) == 1
        plan = catalog.plan(nodes[0], 'Latest')
        assert len(plan.edges) == 1 and plan.target.version == '0.1.77'
        output = args.out / ('automatic-' + version + '.iso')
        result = apply_plan(source, output, plan, catalog, cache=cache)
        assert result.stat().st_size == 1691269120 and sha256_file(result) == EXPECTED
        assert any(n.version == '0.1.77' for n in recognize(result, catalog))
        routes.append(dict(source_version=version, patch=plan.edges[0].asset.name,
            public_download=True, automatic_patch=True, target_recognition=True,
            target_sha256=EXPECTED, target_bytes=result.stat().st_size))
        result.unlink()
        print('Public automatic route ' + version + ' -> 0.1.77: PASS', flush=True)
    report = dict(version='0.1.77', passed=True, retro_trans_version=__version__,
        patcher_commit=subprocess.check_output(['git', '-c', 'safe.directory=' + patcher.as_posix(),
            '-C', str(patcher), 'rev-parse', 'HEAD'], text=True).strip(),
        public_catalog_discovery=True, prior_cached_catalog_immutable=True,
        oversized_patch_withdrawn=True, optimized_full_patch_bytes=14383778,
        routes=routes, target_sha256=EXPECTED, target_bytes=1691269120,
        scope='Public ISO/catalog/engine routes, fresh cache. No emulator, GUI or CHD test.')
    (args.out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
