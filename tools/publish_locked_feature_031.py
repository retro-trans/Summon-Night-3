"""Publish 0.1.31 after isolated runtime verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/locked_feature_candidate_0.1.31').resolve();dst=(ROOT/'work/output/0.1.31').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.31/runtime'
for name in ['final_popup','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['Party Abilities locked-feature popup in English with centered VWF','Popup dismissal and return to map'],
 evidence_sha256=evidence,limitations=['First battle Battle Info menu tested.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['locked_feature031_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Locked Party Abilities popup and return to map.'
for n in ['tools/publish_locked_feature_031.py','tools/locked_feature_runtime_031.py','docs/LOCKED_FEATURE_0.1.31.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.31 ' not in s
entry='''## 0.1.31 — Locked-feature popup translation, 2026-09-27

- Translated the locked-feature popup as "Not available yet."
- Centered its English text using proportional spacing.
- Checked the popup, dismissal and map return
  after a fresh launch with an in-game save. See `docs/LOCKED_FEATURE_0.1.31.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.31 test ISO](work/output/0.1.31/Summon_Night_3_EN_0.1.31.iso)**.
Translates the locked-feature popup with centered proportional text.
See [coverage and test limits](docs/LOCKED_FEATURE_0.1.31.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
