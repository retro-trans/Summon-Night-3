"""Publish 0.1.34 after isolated runtime verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/battle_menu_candidate_0.1.34').resolve();dst=(ROOT/'work/output/0.1.34').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.34/runtime'
for name in ['final_menu','final_info','final_saving','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['All eight battle menu labels','Four Battle Info submenu labels','Two-line system-saving message with VWF','Battle Info return and title-screen return after Suspend save'],
 evidence_sha256=evidence,limitations=['First battle menu and saving flow tested using isolated copied saves.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['battle_menu034_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Battle menus and system-saving popup.'
for n in ['tools/publish_battle_menu_034.py','tools/battle_menu_runtime_034.py','docs/BATTLE_MENU_0.1.34.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.34 ' not in s
entry='''## 0.1.34 — Battle menu and saving-message translation, 2026-09-28

- Translated eight battle-menu labels and four Battle Info labels.
- Translated both system-saving message lines with proportional spacing.
- Checked the battle menus and saving popup
  after a fresh launch with an in-game save. See `docs/BATTLE_MENU_0.1.34.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.34 test ISO](work/output/0.1.34/Summon_Night_3_EN_0.1.34.iso)**.
Translates the battle menus and system-saving notice.
See [coverage and test limits](docs/BATTLE_MENU_0.1.34.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
