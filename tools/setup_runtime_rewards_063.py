"""Preview isolated runtime helpers before writing."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 files={}
 for src,dest in [('tools/launch_report_062.ps1','tools/launch_rewards_063.ps1'),('tools/report_runtime_062.py','tools/rewards_runtime_063.py')]:
  b=(ROOT/src).read_text().replace('0.1.62','0.1.63').replace('report062','rewards063').replace('19398','19399').replace('work/ui/report_0.1.63','work/ui/rewards_0.1.63');files[dest]=b
 for name,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+name+' ('+str(len(b))+' characters)',flush=True)
  if a.write:
   dest=ROOT/name;assert not dest.exists();dest.write_text(b,encoding='utf8')
if __name__=='__main__':main()
