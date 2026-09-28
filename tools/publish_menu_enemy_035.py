"""Publish 0.1.35 after isolated menu-help and enemy-name verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/menu_enemy_candidate_0.1.35').resolve();dst=(ROOT/'work/output/0.1.35').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.35/runtime'
for name in ['final_help','final_enemy','final_status','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['Summon Index battle help on two complete lines','Pirate name with VWF in compact card and full status','Return from status screen'],
 evidence_sha256=evidence,limitations=['First battle runtime verification only; other labels and help records checked statically.'],save_kind='In-game Suspend save from 0.1.34')
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['menu_enemy035_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Summon Index battle help and Pirate name, compact card and full status.'
for n in ['tools/publish_menu_enemy_035.py','tools/menu_enemy_runtime_035.py','docs/MENU_ENEMIES_0.1.35.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.35 ' not in s
entry='''## 0.1.35 — Menu descriptions and generic enemy names, 2026-09-28

- Translated 24 additional menu-help groups, including the separate battle Summon Index description.
- Translated 39 generic enemy labels across 164 references, including Pirate.
- Checked all 58 menu-help references for English text and safe two-line layout.
- Verified Summon Index help and Pirate in compact/full status after a fresh launch
  with a 0.1.34 in-game Suspend save. See `docs/MENU_ENEMIES_0.1.35.md` for coverage.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.35 test ISO](work/output/0.1.35/Summon_Night_3_EN_0.1.35.iso)**.
Translates related menu descriptions and 39 generic enemy names.
See [coverage and test limits](docs/MENU_ENEMIES_0.1.35.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
