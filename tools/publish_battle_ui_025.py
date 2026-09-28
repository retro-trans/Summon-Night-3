"""Verify and publish 0.1.25; preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/battle_ui_candidate_0.1.25').resolve();dst=(ROOT/'work/output/0.1.25').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert len(m['battle_ui025_tables']['graphics']['records'])==8
assert m['battle_ui025_text']['explicit_empty_line_sentinel']
folder=ROOT/'work/ui/battle_ui_0.1.25/runtime';evidence={}
for name in ['final_loaded','final_next','final_notice','final_commands','final_shine_saber']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4, isolated software rendering',
 verified=['Tutorial Next capsule with separate controller icon','Gallery notice and return to player control','Seven translated unit commands','Complete Shine Saber help in proportional text'],
 evidence_sha256=evidence,scope='First pirate battle only',
 limitations=['Gallery notice retains native fixed character spacing.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2))
if not a.write:raise SystemExit
m['battle_ui025_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='First pirate battle; see battle_ui025_runtime.'
for n in ['tools/publish_battle_ui_025.py','tools/battle_ui_runtime_025.py','docs/BATTLE_UI_0.1.25.md','work/ui/battle_ui_0.1.25/graphics.report.json']:
 m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence)
(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
changelog=ROOT/'CHANGELOG.md';text=changelog.read_text(encoding='utf8');assert '## 0.1.25 ' not in text
entry='''## 0.1.25 — battle commands and tutorial prompts, 2026-09-27

- Translated seven unit-command buttons and the tutorial Next graphic.
- Translated the Gallery tutorial notice and Shine Saber description.
- Kept the description within the native help limits; checked its complete
  display with proportional spacing. The notice keeps native fixed spacing.
- Fresh launch with an in-game save verifies the tutorial transition, commands
  and summon help in the first pirate battle. Earlier chapter work is retained.
- See `docs/BATTLE_UI_0.1.25.md` for asset locations and validation limits.

'''
changelog.write_text(text.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
readme=ROOT/'README.md';text=readme.read_text(encoding='utf8')
notice='''Latest build: **[0.1.25 test ISO](work/output/0.1.25/Summon_Night_3_EN_0.1.25.iso)**.
Adds translated battle commands, tutorial Next/notice and Shine Saber help.
See [coverage and test limits](docs/BATTLE_UI_0.1.25.md).
Older progress snapshots below describe their stated versions.

'''
readme.write_text(text.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst)
assert hash_file(dst/m['output_iso'])==m['output_sha256']
print('Published',dst)
