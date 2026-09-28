"""Verify v0.1.35 using Retro Trans's live public catalog and asset download."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--patcher', type=Path, default=ROOT / 'work/scratch/retro-trans-tools-compat')
    parser.add_argument('--out', type=Path, default=ROOT / 'work/scratch/retro-trans-live035')
    args = parser.parse_args()
    sys.path.insert(0, str(args.patcher.resolve()))
    from retro_trans import __version__
    from retro_trans.catalog import refresh_catalog, recognize, apply_plan
    from retro_trans.core import sha256_file
    if args.out.exists():
        raise SystemExit('Choose a fresh output directory.')
    args.out.mkdir(parents=True)
    cache = args.out / 'cache'
    catalog = refresh_catalog(cache=cache)
    records = [r for r in catalog.data['releases'] if r['repo'] == 'retro-trans/Summon-Night-3' and r['tag'] == 'v0.1.35']
    assert len(records) == 1
    print('Public catalog recognition: PASS', flush=True)
    source = ROOT / 'work/source/original.iso'
    recognized = recognize(source, catalog)
    originals = [n for n in recognized if n.game_name == 'Summon Night 3' and n.version == 'original']
    assert len(originals) == 1
    plan = catalog.plan(originals[0], '0.1.35')
    assert len(plan.edges) == 1
    result = apply_plan(source, args.out / 'automatic.iso', plan, catalog, cache=cache)
    digest = sha256_file(result)
    assert digest == '01ae84776c9ad3d5e57bdb6f35291f79b0377f9c1322636703cd6b8544c062db'
    assert result.stat().st_size == 1670623232
    assert any(n.version == '0.1.35' for n in recognize(result, catalog))
    report = dict(retro_trans_version=__version__, patcher_commit=subprocess.check_output(['git', '-C', str(args.patcher), 'rev-parse', 'HEAD'], text=True).strip(), public_catalog_discovery=True, public_asset_download=True, automatic_patch=True, target_recognition=True, target_sha256=digest, target_bytes=result.stat().st_size, scope='ISO; real GitHubClient, fresh cache, bundled engine. No GUI or CHD test.')
    (args.out / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    main()
