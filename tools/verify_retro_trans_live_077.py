"""Verify v0.1.77 using Retro Trans's live public catalog and asset download."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--patcher', type=Path, default=ROOT / 'work/scratch/retro-trans-tools-release073')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/scratch/retro-trans-live077')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print(json.dumps(dict(mode='verify' if args.execute else 'preview',
        destination=str(args.out), repo='retro-trans/Summon-Night-3', tag='v0.1.77',
        routes=['original -> 0.1.77', '0.1.73 -> 0.1.77'],
        public_patch='SN3-English-v0.1.73-to-v0.1.77.xdelta',
        expected_sha256='d35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427'), indent=2), flush=True)
    if not args.execute:
        return
    sys.path.insert(0, str(args.patcher.resolve()))
    from retro_trans import __version__
    from retro_trans.catalog import refresh_catalog, recognize, apply_plan
    from retro_trans.core import sha256_file
    if args.out.exists():
        raise SystemExit('Choose a fresh output directory.')
    args.out.mkdir(parents=True)
    cache = args.out / 'cache'
    catalog = refresh_catalog(cache=cache)
    records = [r for r in catalog.data['releases'] if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.77']
    assert len(records) == 1
    print('Public catalog recognition: PASS', flush=True)
    original = ROOT / 'work/source/original.iso'
    original_nodes = [n for n in recognize(original, catalog) if n.game_name == 'Summon Night 3' and n.version == 'original']
    assert len(original_nodes) == 1
    original_plan = catalog.plan(original_nodes[0], 'Latest')
    assert len(original_plan.edges) == 1 and original_plan.target.version == '0.1.77'
    source = ROOT / 'work/output/0.1.73/Summon_Night_3_EN_0.1.73.iso'
    recognized = recognize(source, catalog)
    originals = [n for n in recognized if n.game_name == 'Summon Night 3' and n.version == '0.1.73']
    assert len(originals) == 1
    plan = catalog.plan(originals[0], 'Latest')
    assert plan.target.version == '0.1.77'
    assert len(plan.edges) == 1
    result = apply_plan(source, args.out / 'automatic.iso', plan, catalog, cache=cache)
    digest = sha256_file(result)
    assert digest == 'd35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427'
    assert result.stat().st_size == 1691269120
    assert any(n.version == '0.1.77' for n in recognize(result, catalog))
    report = dict(retro_trans_version=__version__, patcher_commit=subprocess.check_output(['git', '-c', 'safe.directory=' + args.patcher.resolve().as_posix(), '-C', str(args.patcher), 'rev-parse', 'HEAD'], text=True).strip(), public_catalog_discovery=True, original_latest_route=True, upgrade_source_version="0.1.73", public_asset_download=True, automatic_patch=True, target_recognition=True, target_sha256=digest, target_bytes=result.stat().st_size, scope='ISO; real GitHubClient, fresh cache, bundled engine. No GUI or CHD test.')
    (args.out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    main()
