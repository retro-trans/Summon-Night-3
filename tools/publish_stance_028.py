"""Publish the verified 0.1.28 candidate; dry-run before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/stance_candidate_0.1.28').resolve();dst=(ROOT/'work/output/0.1.28').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert not m['stance028_text']['entries'] and not m['stance028_text']['skipped']
assert sum(len(t['changes']) for t in m['stance028_tables']['tables'])==len(json.loads((ROOT/'work/translation/en/stance_0.1.28/meaning_review.json').read_text())['entries'])
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.28/runtime'
for name in ['final_loaded','final_stance_open','final_counter','final_confirm','final_reopen','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
diagnosis=ROOT/'work/ui/ui_fixes_0.1.28/diagnosis.json';evidence[diagnosis.relative_to(ROOT).as_posix()]=hash_file(diagnosis)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4, isolated software rendering',
 verified=['Opening Stance without crashing','Guard and Counter descriptions fit','Selecting a stance and reopening the submenu','Returning to map control'],
 evidence_sha256=evidence,limitations=['First pirate battle Guard/Counter tested live; other stance descriptions statically checked.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2))
if not a.write:raise SystemExit
m['stance028_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='First pirate battle Stance open, change, reopen and return; see stance028_runtime.'
for n in ['tools/publish_stance_028.py','tools/ui_fixes_runtime_028.py','docs/STANCE_FIX_0.1.28.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.28 ' not in s
entry='''## 0.1.28 — Stance crash fix, 2026-09-27

- Fixed oversized stance descriptions and missing end markers that made
  opening the Stance submenu overrun the native text buffers.
- Added bounded two-line descriptions and checked related stance records.
- Verified Guard/Counter selection, reopening and return to play from a fresh
  launch with an in-game save. See `docs/STANCE_FIX_0.1.28.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.28 test ISO](work/output/0.1.28/Summon_Night_3_EN_0.1.28.iso)**.
Fixes the crash when opening Stance.
See [coverage and test limits](docs/STANCE_FIX_0.1.28.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
