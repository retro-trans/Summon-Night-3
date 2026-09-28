"""Publish 0.1.30 after isolated runtime verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/battle_help_candidate_0.1.30').resolve();dst=(ROOT/'work/output/0.1.30').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.30/runtime'
for name in ['final_party','final_support','final_brave','final_winlose','final_conditions','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['All four Battle Info descriptions','Win/Lose condition popup','Return to map'],
 evidence_sha256=evidence,limitations=['First battle Battle Info menu tested.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['battle_help030_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Battle Info descriptions, conditions popup, map return.'
for n in ['tools/publish_battle_help_030.py','tools/battle_help_runtime_030.py','docs/BATTLE_HELP_0.1.30.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.30 ' not in s
entry='''## 0.1.30 — Battle Info help wrapping, 2026-09-27

- Fixed the split word and missing spacing in the Win/Lose description.
- Fixed Party Abilities help to fit the actual 27-cell display limit.
- Checked all four Battle Info descriptions, conditions popup and map return
  after a fresh launch with an in-game save. See `docs/BATTLE_HELP_0.1.30.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.30 test ISO](work/output/0.1.30/Summon_Night_3_EN_0.1.30.iso)**.
Fixes Win/Lose and Party Abilities description wrapping.
See [coverage and test limits](docs/BATTLE_HELP_0.1.30.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
