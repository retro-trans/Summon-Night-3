"""Publish 0.1.33 after isolated runtime verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/magic_heading_candidate_0.1.33').resolve();dst=(ROOT/'work/output/0.1.33').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.33/runtime'
for name in ['final_dritol','final_shine','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['Dritol battle magic heading translated with VWF','Shine Saber heading and spell list','Return to unit commands'],
 evidence_sha256=evidence,limitations=['First battle Dritol and Shine Saber headings tested; other names covered by static lookup checks.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['magic_heading033_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Battle magic headings and return to commands.'
for n in ['tools/publish_magic_heading_033.py','tools/magic_heading_runtime_033.py','docs/MAGIC_HEADING_0.1.33.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.33 ' not in s
entry='''## 0.1.33 — Battle magic heading translation, 2026-09-28

- Applied existing saved-name translations to the battle magic heading.
- Added proportional rendering for the heading; custom names and saves are preserved.
- Checked Dritol, Shine Saber and return to commands
  after a fresh launch with an in-game save. See `docs/MAGIC_HEADING_0.1.33.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.33 test ISO](work/output/0.1.33/Summon_Night_3_EN_0.1.33.iso)**.
Translates summon names in the battle magic heading, including older saves.
See [coverage and test limits](docs/MAGIC_HEADING_0.1.33.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
