"""Verify and publish 0.1.26; preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/ui_fixes_candidate_0.1.26_release').resolve();dst=(ROOT/'work/output/0.1.26').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
assert len(m['ui_fixes026_tables']['graphics']['records'])==4
assert m['ui_fixes026_text']['stat_spacing']
folder=ROOT/'work/ui/ui_fixes_0.1.26/runtime';evidence={}
for name in ['final_loaded','final_inventory','final_favorites','final_spell','final_kyle']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4, isolated software rendering',
 verified=['Inventory AT+17 spacing','Locked spell restriction with question marks retained','Shine Saber ability name clear of MP cost','Kyle English portrait nameplate'],
 evidence_sha256=evidence,scope='First pirate battle only',
 limitations=['First pirate battle and available saved-game menus; no full playthrough.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2))
if not a.write:raise SystemExit
m['ui_fixes026_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='First pirate battle; see ui_fixes026_runtime.'
for n in ['tools/publish_ui_fixes_026.py','tools/ui_fixes_runtime_026.py','docs/UI_FIXES_0.1.26.md']:
 m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence)
(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
changelog=ROOT/'CHANGELOG.md';text=changelog.read_text(encoding='utf8');assert '## 0.1.26 ' not in text
entry='''## 0.1.26 — remaining summon labels and Kyle nameplate, 2026-09-27

- Translated the locked-spell Favorites Only restriction while preserving its
  question marks, and added Shine Saber's attack name with proportional text.
- Replaced Kyle's portrait nameplate and shadow layer with English lettering.
- Corrected inventory stat-value spacing; retained the existing text VWF.
- Fresh-launch testing uses a copied in-game save. See
  `docs/UI_FIXES_0.1.26.md` for scope and evidence.

'''
changelog.write_text(text.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
readme=ROOT/'README.md';text=readme.read_text(encoding='utf8')
notice='''Latest build: **[0.1.26 test ISO](work/output/0.1.26/Summon_Night_3_EN_0.1.26.iso)**.
Adds the remaining summon labels, Kyle nameplate and inventory spacing fix.
See [coverage and test limits](docs/UI_FIXES_0.1.26.md).
Older progress snapshots below describe their stated versions.

'''
readme.write_text(text.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst)
assert hash_file(dst/m['output_iso'])==m['output_sha256']
print('Published',dst)
