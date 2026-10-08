"""Package the verified local 073-to-077 test upgrade with Retro Trans Tools."""
import argparse,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 sys.path.insert(0,str(ROOT/'work/scratch/retro-trans-tools-release073'))
 from retro_trans.release import build_release,validate_directory
 from retro_trans.core import sha256_file
 destination=ROOT/'work/output/summon-test-v0.1.77'
 source=ROOT/'work/output/0.1.73/Summon_Night_3_EN_0.1.73.iso'
 target=ROOT/'work/output/0.1.77/Summon_Night_3_EN_0.1.77.iso'
 m=json.loads((target.parent/'manifest.json').read_text());old=json.loads((source.parent/'manifest.json').read_text())
 assert sha256_file(target)==m['output_sha256'] and sha256_file(source)==old['output_sha256']
 for name in ('stability-report.json','runtime-validation.json','battle-validation.json'):
  check=json.loads((target.parent/name).read_text());assert check['passed'],name
  assert check['iso_sha256']==m['output_sha256'],name
 config=dict(game_id='summon-night-3',game_name='Summon Night 3',platform='PSP',version='0.1.77',
  source_commit=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],text=True).strip(),
  patches=[dict(patch='SN3-English-v0.1.73-to-v0.1.77.xdelta',edition='Japanese NPJH50380',language='en',
   source_version='0.1.73',source_format='iso',target_format='iso',source=str(source),target=str(target))])
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(destination))),flush=True)
 if not a.write:return
 path=ROOT/'work/scratch/battle077-test-config.json';path.write_text(json.dumps(config,indent=2),encoding='utf8')
 build_release(path,destination,cache=ROOT/'work/scratch/release073-cache')
 extras={'README-v0.1.77.txt':ROOT/'docs/BATTLE_UI_0.1.77.md',
         'CHANGELOG-v0.1.77.txt':ROOT/'CHANGELOG.md',
         'GAMEPLAY-VALIDATION-v0.1.77.json':target.parent/'runtime-validation.json'}
 for name,file in extras.items():(destination/name).write_bytes(file.read_bytes())
 files=sorted(p for p in destination.iterdir() if p.is_file() and p.name!='SHA256SUMS.txt')
 (destination/'SHA256SUMS.txt').write_text(''.join(sha256_file(p)+'  '+p.name+'\n' for p in files))
 validate_directory(destination)
 archive=ROOT/'work/output/SN3-English-test-v0.1.77.zip';assert not archive.exists()
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for file in sorted(destination.iterdir()):
   if file.is_file():z.write(file,file.name)
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  assert {p.name for p in destination.iterdir() if p.is_file()}==set(z.namelist())
 print(json.dumps(dict(archive=str(archive),sha256=sha256_file(archive),roundtrip_verified=True)),flush=True)

if __name__=='__main__':main()

