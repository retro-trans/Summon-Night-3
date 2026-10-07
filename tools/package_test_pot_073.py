"""Create a local 0.1.65-to-0.1.73 Retro Trans upgrade after gameplay checks."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 sys.path.insert(0,str(ROOT/'work/scratch/retro-trans-tools-release041'))
 from retro_trans.release import build_release,validate_directory
 from retro_trans.core import sha256_file
 destination=ROOT/'work/output/summon-test-v0.1.73'
 source=ROOT/'work/output/0.1.65/Summon_Night_3_EN_0.1.65.iso'
 target=ROOT/'work/output/0.1.73/Summon_Night_3_EN_0.1.73.iso'
 m=json.loads((target.parent/'manifest.json').read_text())
 old=json.loads((source.parent/'manifest.json').read_text())
 assert sha256_file(target)==m['output_sha256']
 assert sha256_file(source)==old['output_sha256']
 for name in ('stability-report.json','runtime-validation.json','name-cache-validation.json'):
  check=json.loads((target.parent/name).read_text());assert check['passed'],name
  if 'iso_sha256' in check:assert check['iso_sha256']==m['output_sha256']
 config=dict(game_id='summon-night-3',game_name='Summon Night 3',platform='PSP',version='0.1.73',
  source_commit=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],text=True).strip(),
  patches=[dict(patch='SN3-English-v0.1.65-to-v0.1.73.xdelta',edition='Japanese NPJH50380',language='en',
   source_version='0.1.65',source_format='iso',target_format='iso',source=str(source),target=str(target))])
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(destination),config=config)),flush=True)
 if not a.write:return
 config_path=ROOT/'work/scratch/pot073-test-config.json';config_path.write_text(json.dumps(config,indent=2),encoding='utf8')
 build_release(config_path,destination,cache=ROOT/'work/scratch/release041-cache')
 validate_directory(destination)
 print('Local upgrade passed Retro Trans validation and full round-trip verification.',flush=True)
if __name__=='__main__':main()
