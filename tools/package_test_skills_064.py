"""Create a local 0.1.55-to-0.1.64 upgrade with Retro Trans round-trip checks."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 sys.path.insert(0,str(ROOT/'work/scratch/retro-trans-tools-release041'))
 from retro_trans.release import build_release,validate_directory
 from retro_trans.core import sha256_file
 destination=ROOT/'work/output/skills-test-v0.1.64'
 source=ROOT/'work/output/0.1.55/Summon_Night_3_EN_0.1.55.iso'
 target=ROOT/'work/output/0.1.64/Summon_Night_3_EN_0.1.64.iso'
 m=json.loads((target.parent/'manifest.json').read_text())
 assert sha256_file(target)==m['output_sha256']
 assert sha256_file(source)=='d75654f7d9381293b8b78e8e7ddd8766bd2c518e9da05a8a7983205abd04bfe9'
 stability=json.loads((target.parent/'stability-report.json').read_text())
 assert stability['passed'] and stability['iso_sha256']==m['output_sha256']
 config=dict(game_id='summon-night-3',game_name='Summon Night 3',platform='PSP',version='0.1.64',
  source_commit=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse','HEAD'],text=True).strip(),
  patches=[dict(patch='SN3-English-v0.1.55-to-v0.1.64.xdelta',edition='Japanese NPJH50380',language='en',
   source_version='0.1.55',source_format='iso',target_format='iso',source=str(source),target=str(target))])
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(destination),config=config)),flush=True)
 if not a.write:return
 config_path=ROOT/'work/scratch/skills064-test-config.json'
 config_path.write_text(json.dumps(config,indent=2),encoding='utf8')
 build_release(config_path,destination,cache=ROOT/'work/scratch/release041-cache')
 validate_directory(destination)
 print('Local upgrade passed Retro Trans validation and full round-trip verification.',flush=True)

if __name__=='__main__':main()
