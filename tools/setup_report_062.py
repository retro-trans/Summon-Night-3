"""Preview derived build, regression, package and runtime helpers before writing."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();files={}
 b=(ROOT/'tools/build_report_061.py').read_text().replace('0.1.61','0.1.62').replace('_061','_062').replace('report061','report062').replace('0.1.60','0.1.61')
 b=b.replace("+[ROOT/'work/ui/report_0.1.62/yard_generated.png',ROOT/'work/ui/report_0.1.62/map_generated.png',ROOT/'work/ui/report_0.1.62/imagegen.json']",'')
 files['tools/build_report_062.py']=b
 b=(ROOT/'tools/package_test_report_061.py').read_text().replace('0.1.61','0.1.62').replace('report061','report062');files['tools/package_test_report_062.py']=b
 b=(ROOT/'tools/launch_report_061.ps1').read_text().replace('0.1.61','0.1.62').replace('report061','report062').replace('19397','19398');files['tools/launch_report_062.ps1']=b
 b=(ROOT/'tools/report_runtime_061.py').read_text().replace('0.1.61','0.1.62').replace('report061','report062').replace('19397','19398');files['tools/report_runtime_062.py']=b
 for name,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+name+' ('+str(len(b))+' characters)',flush=True)
  if a.write:
   dest=ROOT/name;assert not dest.exists();dest.write_text(b,encoding='utf8')
if __name__=='__main__':main()
