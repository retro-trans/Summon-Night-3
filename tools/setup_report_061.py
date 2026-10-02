"""Preview derived build/package/runtime helpers before creating them."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();files={}
 b=(ROOT/'tools/build_levelup_060.py').read_text().replace('from levelup_060 import','from report_ui_061 import').replace("BASE=ROOT/'work/output/0.1.59'","BASE=ROOT/'work/output/0.1.60'")
 b=b.replace('0.1.60','0.1.61').replace("BASE=ROOT/'work/output/0.1.61'","BASE=ROOT/'work/output/0.1.60'").replace("comparison_build='0.1.59'","comparison_build='0.1.60'")
 b=b.replace("['build_levelup_060.py','levelup_060.py','verify_levelup_060.py']","['build_report_061.py','report_ui_061.py','verify_report_061.py','verify_stability_061.py','draft_report_061.py']")
 b=b.replace('work/translation/en/levelup_0.1.61','work/translation/en/report_0.1.61').replace("[ROOT/'work/ui/levelup_0.1.61/levelup_generated.png',ROOT/'work/ui/levelup_0.1.61/imagegen.json']","[ROOT/'work/ui/report_0.1.61/yard_generated.png',ROOT/'work/ui/report_0.1.61/map_generated.png',ROOT/'work/ui/report_0.1.61/imagegen.json']")
 b=b.replace("master=repack(master,{0:p01['index_bytes'],1:p02['index_bytes']})","master=repack(master,{0:p01['index_bytes'],1:p02['index_bytes'],7:tables02[3]})").replace('levelup060_header','report061_ui')
 b=b.replace('"""Build summon-screen heading and proportional control hints on immutable 0.1.59."""','"""Build reported UI fixes on immutable 0.1.60."""');files['tools/build_report_061.py']=b
 b=(ROOT/'tools/package_test_levelup_060.py').read_text().replace('0.1.60','0.1.61').replace('levelup-test','report-test').replace('levelup060','report061');files['tools/package_test_report_061.py']=b
 b=(ROOT/'tools/launch_levelup_060.ps1').read_text().replace('0.1.60','0.1.61').replace('levelup060','report061').replace('19396','19397');files['tools/launch_report_061.ps1']=b
 b=(ROOT/'tools/levelup_runtime_060.py').read_text().replace('0.1.60','0.1.61').replace('levelup060','report061').replace('19396','19397').replace('work/ui/levelup_0.1.61','work/ui/report_0.1.61');files['tools/report_runtime_061.py']=b
 for name,text in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+name+' ('+str(len(text))+' characters)',flush=True)
  if a.write:
   dest=ROOT/name;assert not dest.exists();dest.write_text(text,encoding='utf8')
if __name__=='__main__':main()
