"""Publish the verified 0.1.29 candidate; dry-run before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/deployment_candidate_0.1.29_final').resolve();dst=(ROOT/'work/output/0.1.29').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert not m['deployment029_text']['entries'] and not m['deployment029_text']['skipped']
assert not m['deployment029_tables']['tables']
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.29/runtime'
for name in ['final_aty','final_soldier','final_gear','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
layout=ROOT/'work/ui/ui_fixes_0.1.29/layout.json';evidence[layout.relative_to(ROOT).as_posix()]=hash_file(layout)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4, isolated software rendering',
 verified=['Proportional name, class, attack and stance fields','Support description with proportional chunk spacing','Shortcut icons aligned with Deploy, Status/Gear and Map','Soldier and equipment views, return to map'],
 evidence_sha256=evidence,limitations=['First battle Aty and Soldier deployment views tested; other support descriptions not exercised in-game.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2))
if not a.write:raise SystemExit
m['deployment029_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Deployment Aty, Soldier, equipment and map return; see deployment029_runtime.'
for n in ['tools/publish_deployment_029.py','tools/deployment_runtime_029.py','docs/DEPLOYMENT_0.1.29.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.29 ' not in s
entry='''## 0.1.29 — Deployment VWF and shortcut alignment, 2026-09-27

- Applied proportional spacing to deployment name, class, attack and stance.
- Packed support-skill description chunks with proportional spacing.
- Aligned the Deploy, Status/Gear and Map icons with their labels.
- Verified Aty, Soldier, equipment view and return to map after a fresh launch.
  See `docs/DEPLOYMENT_0.1.29.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.29 test ISO](work/output/0.1.29/Summon_Night_3_EN_0.1.29.iso)**.
Adds Deployment VWF and aligns shortcut icons with their labels.
See [coverage and test limits](docs/DEPLOYMENT_0.1.29.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
