"""Publish 0.1.32 after isolated runtime verification. Preview before --write."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file
p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
src=(ROOT/'work/scratch/confirm_candidate_0.1.32').resolve();dst=(ROOT/'work/output/0.1.32').resolve()
assert ROOT in src.parents and ROOT in dst.parents and not dst.exists()
m=json.loads((src/'manifest.json').read_text());assert hash_file(src/m['output_iso'])==m['output_sha256']
for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
evidence={};folder=ROOT/'work/ui/ui_fixes_0.1.32/runtime'
for name in ['final_no','final_yes','final_return']:
 for ext in ('.png','.json'):
  f=folder/(name+ext);evidence[f.relative_to(ROOT).as_posix()]=hash_file(f)
runtime=dict(iso_sha256=m['output_sha256'],fresh_launch=True,in_game_save=True,save_state=False,
 emulator='PPSSPP 1.20.4 isolated software rendering',
 verified=['Start battle prompt and Yes/No proportional text','Cursor on both choices','No cancels and returns to preparation menu'],
 evidence_sha256=evidence,limitations=['First battle Start Battle confirmation tested; Yes was highlighted but not activated.'])
print(json.dumps(dict(destination=str(dst),sha256=m['output_sha256'],runtime=runtime),indent=2),flush=True)
if not a.write:raise SystemExit
m['confirm032_runtime']=runtime;m['static_validation']['runtime_verified']=True
m['static_validation']['runtime_scope']='Start Battle confirmation, both choices and cancellation.'
for n in ['tools/publish_confirm_vwf_032.py','tools/confirm_runtime_032.py','docs/CONFIRM_VWF_0.1.32.md']:m['inputs_sha256'][n]=hash_file(ROOT/n)
m['inputs_sha256'].update(evidence);(src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
f=ROOT/'CHANGELOG.md';s=f.read_text(encoding='utf8');assert '## 0.1.32 ' not in s
entry='''## 0.1.32 — Start Battle confirmation VWF, 2026-09-27

- Applied proportional spacing to "Start battle?", "Yes" and "No".
- Centered all three lines and retained the native choice behavior.
- Checked both cursor positions and cancellation
  after a fresh launch with an in-game save. See `docs/CONFIRM_VWF_0.1.32.md`.

'''
f.write_text(s.replace('# Changelog\n\n','# Changelog\n\n'+entry,1),encoding='utf8')
f=ROOT/'README.md';s=f.read_text(encoding='utf8')
notice='''Latest build: **[0.1.32 test ISO](work/output/0.1.32/Summon_Night_3_EN_0.1.32.iso)**.
Adds VWF to the Start Battle confirmation prompt and choices.
See [coverage and test limits](docs/CONFIRM_VWF_0.1.32.md).
Older progress snapshots below describe their stated versions.

'''
f.write_text(s.replace('# Summon Night 3 translation\n\n','# Summon Night 3 translation\n\n'+notice,1),encoding='utf8')
src.rename(dst);assert hash_file(dst/m['output_iso'])==m['output_sha256'];print('Published',dst)
