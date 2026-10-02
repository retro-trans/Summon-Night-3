"""Preview isolated PPSSPP helpers before creating them."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 for src,dest in [('tools/launch_rewards_063.ps1','tools/launch_skills_064.ps1'),('tools/rewards_runtime_063.py','tools/skills_runtime_064.py')]:
  b=(ROOT/src).read_text().replace('0.1.63','0.1.64').replace('rewards063','skills064').replace('19399','19400').replace('work/ui/rewards_0.1.64','work/ui/skills_0.1.64')
  print(('WRITE ' if a.write else 'PREVIEW ')+dest+' ('+str(len(b))+' characters)',flush=True)
  if a.write:
   path=ROOT/dest;assert not path.exists();path.write_text(b,encoding='utf8')
if __name__=='__main__':main()
