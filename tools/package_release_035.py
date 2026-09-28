"""Verify the v0.1.35 delta round trip; preview metadata before --write."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'work/output/release-v0.1.35'

def hashes(path):
 h1=hashlib.sha1();h2=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h1.update(b);h2.update(b)
 return dict(bytes=path.stat().st_size,sha1=h1.hexdigest(),sha256=h2.hexdigest())

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 m=json.loads((ROOT/'work/output/0.1.35/manifest.json').read_text())
 source=hashes(ROOT/'work/source/original.iso')
 target=hashes(ROOT/'work/output/0.1.35'/m['output_iso'])
 rebuilt=hashes(ROOT/'work/scratch/release035_roundtrip.iso')
 patchname='SN3-English-v0.1.35.xdelta';patch=hashes(OUT/patchname)
 assert source['sha256']==m['source_iso_sha256']
 assert target['sha256']==m['output_sha256'] and rebuilt==target
 report=dict(version='0.1.35',build_revision='Initial GitHub release; menu help and generic enemy names, cumulative translation retained',
  patches=[dict(edition='Japanese PSP NPJH50380',patch=patchname,source_version='Japanese',source_sha256=source['sha256'],source_sha1=source['sha1'],source_bytes=source['bytes'],target_sha256=target['sha256'],target_sha1=target['sha1'],target_bytes=target['bytes'],patch_sha256=patch['sha256'],patch_sha1=patch['sha1'],patch_bytes=patch['bytes'],roundtrip_verified=True)],
  validation=dict(bank_indexes=23,unchanged_resources=5728,additional_help_groups=24,generic_enemy_labels=39,enemy_references=164,menu_help_references_checked=58),
  runtime_testing='PPSSPP 1.20.4 software renderer, fresh launch, v0.1.34 in-game Suspend save. First-battle Summon Index help, Pirate compact/full status, and return verified. Other entries statically checked; no full route playthrough or PSP hardware test.',
  game_build_manifest_sha256=hashes(ROOT/'work/output/0.1.35/manifest.json')['sha256'],
  scope_report='docs/MENU_ENEMIES_0.1.35.md',delta_tool='xdelta3 3.1.0',translation_status='Incomplete; AI-assisted')
 readme=f'''Summon Night 3 English v0.1.35
Japanese PSP release NPJH50380 — incomplete translation test release

PATCH YOUR OWN JAPANESE ISO
Patch: {patchname}
Source size: {source['bytes']:,} bytes
Source SHA256: {source['sha256']}
Source SHA1: {source['sha1']}
Output size: {target['bytes']:,} bytes
Output SHA256: {target['sha256']}
Output SHA1: {target['sha1']}

APPLY
Use Retro Trans manual Apply xdelta, DeltaPatcher, or:
xdelta3 -d -s "Summon Night 3 (Japan).iso" "{patchname}" "Summon Night 3 English v0.1.35.iso"

Use an unpacked ISO, not a ZIP/CSO/CHD or previous English build. Keep checksum
verification enabled. Automatic catalog detection has not been verified.
Start the patched ISO fresh and load an in-game save, not an emulator save state.

VALIDATION
The patch was decoded against the original ISO and its complete output hashes
match the tested build. All 23 archive indexes and 5,728 unchanged resources
passed build checks. The first battle's Summon Index help and Pirate compact
and full status were checked in PPSSPP 1.20.4 with an older in-game Suspend save.
Other translated entries received static checks, not individual gameplay tests.

SCOPE
24 additional menu-help groups and 39 generic enemy names in v0.1.35; earlier
identified story and battle resources through Chapter 8, selected shared and
optional dialogue, and ongoing UI/VWF work retained. Not a full translation
or a complete route playthrough. Some classes, equipment, named creatures and
graphical labels remain Japanese or untested. PSP hardware is untested.
AI-assisted translation; no audited human-proofreading line count is available.

FILES
CHANGELOG-v0.1.35.txt: project history.
BUILD-MANIFEST-v0.1.35.json: source, output and patch identities and checks.
SHA1SUMS-v0.1.35.txt / SHA256SUMS-v0.1.35.txt: asset checksums.

SOURCE AND REPORTING
https://github.com/retro-trans/Summon-Night-3
https://github.com/retro-trans/Summon-Night-3/issues
GitHub Source code downloads contain project files, not the game or patch.
Report patch/emulator versions, chapter, steps, screenshot and save method.

No complete game image is included. Use your own copy. The patch is free;
do not sell it or prepatched game images.
'''
 contents={'README-v0.1.35.txt':readme,'CHANGELOG-v0.1.35.txt':(ROOT/'CHANGELOG.md').read_text(encoding='utf8'),'BUILD-MANIFEST-v0.1.35.json':json.dumps(report,indent=2)+'\n'}
 print(json.dumps(dict(mode='write' if a.write else 'preview',patch=patch,source=source,target=target,roundtrip_verified=True,assets=[patchname,*contents,'SHA1SUMS-v0.1.35.txt','SHA256SUMS-v0.1.35.txt']),indent=2),flush=True)
 if not a.write:return
 for name,s in contents.items():
  path=OUT/name;assert not path.exists(),path;path.write_text(s,encoding='utf8')
 files=[OUT/patchname,*[OUT/n for n in contents]]
 hs={f.name:hashes(f) for f in files}
 for alg in ('sha1','sha256'):
  (OUT/f'{alg.upper()}SUMS-v0.1.35.txt').write_text(''.join(f'{v[alg]}  {name}\n' for name,v in sorted(hs.items())),encoding='ascii')
 print('Release assets verified and written.')
if __name__=='__main__':main()
