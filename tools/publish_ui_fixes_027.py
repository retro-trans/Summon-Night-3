"""Publish the verified 0.1.27 candidate; dry-run before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/ui_fixes_candidate_0.1.27_verified').resolve();dst=(ROOT/'work/output/0.1.27').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert len(m['ui_fixes027_text']['entries'])==23 and not m['ui_fixes027_text']['skipped']
assert sum(len(t['changes']) for t in m['ui_fixes027_tables']['tables'])==10
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.27/runtime'
for name in ['final_loaded','final_notice','final_skill','final_return','final_inventory']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4, isolated software rendering',
 verified=['Centered proportional Gallery tutorial notice','Pact Ritual: Machine name and Machine/Neutral crafting help','Return from skill menu to player control','Inventory AT+17 retains native symbolic spacing'],
 evidence_sha256=evidence,limitations=['First pirate battle only; other ritual variants were statically verified, not exercised in-game.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2))
if not a.write:raise SystemExit
m['ui_fixes027_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='First pirate battle tutorial notice and Machine ritual menu; see ui_fixes027_runtime.'
for n in ['tools/publish_ui_fixes_027.py','tools/ui_fixes_runtime_027.py','docs/UI_FIXES_0.1.27.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.27 ' not in s
entry='''## 0.1.27 — tutorial notice VWF and Pact Ritual, 2026-09-27

- Centered the Gallery tutorial notice using proportional letter spacing.
- Translated Pact Ritual skill names, including 15 single and combined affinity variants,
  and the dynamically assembled summon-crafting description.
- Verified the notice, Machine/Neutral skill menu and return to play from a
  fresh launch with an in-game save. See `docs/UI_FIXES_0.1.27.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.27 test ISO](work/output/0.1.27/Summon_Night_3_EN_0.1.27.iso)**.
Adds proportional tutorial-notice text and translated Pact Ritual UI.
See [coverage and test limits](docs/UI_FIXES_0.1.27.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
