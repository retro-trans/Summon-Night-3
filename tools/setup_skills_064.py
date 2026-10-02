"""Preview new translation/build helpers before creating them."""
import argparse,json
from sn3_archive import ROOT
from skills_064 import TEXT,draft
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 files={TEXT.relative_to(ROOT).as_posix():json.dumps(draft(),ensure_ascii=False,indent=2)+'\n'}
 b=(ROOT/'tools/build_rewards_063.py').read_text().replace('0.1.63','0.1.64').replace('0.1.62','0.1.63').replace('rewards_063','skills_064').replace('verify_stability_063','verify_stability_064').replace('rewards063_ui','skills064_ui').replace('work/translation/en/rewards_0.1.64','work/translation/en/skills_0.1.64')
 files['tools/build_skills_064.py']=b
 b=(ROOT/'tools/package_test_rewards_063.py').read_text().replace('0.1.63','0.1.64').replace('rewards063','skills064').replace('rewards-test','skills-test');files['tools/package_test_skills_064.py']=b
 for n,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+n+' ('+str(len(b))+' characters)',flush=True)
  if n.endswith('strings.json'):print(b,flush=True)
  if a.write:
   dest=ROOT/n;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(b,encoding='utf8')
if __name__=='__main__':main()
