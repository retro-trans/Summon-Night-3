"""Preview derivative build and isolated release QA helpers before writing."""
import argparse,json
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();files={}
 b=(ROOT/'tools/build_skills_064.py').read_text().replace('0.1.64','0.1.65').replace('0.1.63','0.1.64').replace('skills_064','cache_065').replace('skills064_ui','cache065_arena').replace('setup_skills_064','setup_cache_065')
 files['tools/build_cache_065.py']=b
 for stem,suffix in [('launch_release','ps1'),('release_runtime','py'),('record_release_runtime','py'),('package_release','py')]:
  b=(ROOT/f'tools/{stem}_064.{suffix}').read_text().replace('0.1.64','0.1.65').replace('release064','release065').replace('19401','19402')
  files[f'tools/{stem}_065.{suffix}']=b
 b=(ROOT/'tools/stage_release_064.py').read_text().replace('0.1.64','0.1.65').replace('06[0-4]','06[0-5]').replace('6[0-4]','6[0-5]')
 files['tools/stage_release_065.py']=b
 for n,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+n+' '+str(len(b))+' characters')
  if a.write:
   path=ROOT/n;assert not path.exists();path.write_text(b,encoding='utf8')
if __name__=='__main__':main()
