"""Preview release helpers and notes before writing new files."""
import argparse,json
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 files={}
 for src,dest in [('tools/launch_skills_064.ps1','tools/launch_release_064.ps1'),('tools/skills_runtime_064.py','tools/release_runtime_064.py')]:
  b=(ROOT/src).read_text().replace('skills064','release064').replace('19400','19401').replace('work/ui/skills_0.1.64','work/ui/release_0.1.64');files[dest]=b
 b=(ROOT/'tools/record_release_runtime_055.py').read_text().replace('0.1.55','0.1.64').replace('battle_0.1.64','release_0.1.64').replace('release055','release064').replace("runtime/'release064.log'","runtime/'runtime.log'")
 b=b.replace("'Known Extra Brave Goal mystery-row overflow and Japanese Summon Index descriptions remain.'","'Exact recently reported reward/recruitment, map, casting banner, Level Up and Learn Skills screens still require matching saves.'")
 files['tools/record_release_runtime_064.py']=b
 b=(ROOT/'tools/package_release_055.py').read_text().replace('0.1.55','0.1.64').replace('0.1.54','0.1.55').replace('release055','release064');files['tools/package_release_064.py']=b
 b=(ROOT/'tools/verify_retro_trans_live_055.py').read_text().replace('0.1.55','0.1.64').replace('0.1.54','0.1.55').replace('live055','live064').replace('d75654f7d9381293b8b78e8e7ddd8766bd2c518e9da05a8a7983205abd04bfe9','a1732872533cbadaa01f7c117fbddb012e31f0b7de5c7b03733a74d4990dcbe3')
 m=json.loads((ROOT/'work/output/0.1.64/manifest.json').read_text());b=b.replace('1676998656',str(m['output_size_bytes']));files['tools/verify_retro_trans_live_064.py']=b
 for n,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+n+' ('+str(len(b))+' characters)',flush=True)
  if a.write:
   path=ROOT/n;assert not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_text(b,encoding='utf8')
if __name__=='__main__':main()
