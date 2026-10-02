"""Preview translation and derived build/package helpers before writes."""
import argparse,json
from sn3_archive import ROOT
from rewards_063 import TEXT,draft
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 files={str(TEXT.relative_to(ROOT)):json.dumps(draft(),ensure_ascii=False,indent=2)+'\n'}
 b=(ROOT/'tools/build_report_062.py').read_text().replace('0.1.62','0.1.63').replace('0.1.61','0.1.62').replace('report_ui_062','rewards_063').replace('build_report_062','build_rewards_063').replace('verify_report_062','verify_rewards_063').replace('verify_stability_062','verify_stability_063').replace('draft_report_062','setup_rewards_063').replace('report062_ui','rewards063_ui').replace('work/translation/en/report_0.1.63','work/translation/en/rewards_0.1.63')
 files['tools/build_rewards_063.py']=b
 b=(ROOT/'tools/package_test_report_062.py').read_text().replace('0.1.62','0.1.63').replace('report062','rewards063').replace('report-test','rewards-test');files['tools/package_test_rewards_063.py']=b
 for name,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+name+' ('+str(len(b))+' characters)',flush=True)
  if name.endswith('strings.json'):print(b,flush=True)
  if a.write:
   dest=ROOT/name;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(b,encoding='utf8')
if __name__=='__main__':main()
