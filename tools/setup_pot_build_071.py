"""Create the new local builder without modifying historical build inputs."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 before=(ROOT/'tools/build_cache_065.py').read_text()
 after=before.replace('reported UI fixes on immutable 0.1.64','summon name-cache crash fix on immutable 0.1.70')
 after=after.replace('from cache_065 import','from pot_fix_071 import').replace("0.1.64","0.1.70").replace("0.1.65","0.1.71")
 after=after.replace("['build_cache_065.py','cache_065.py','verify_cache_065.py','verify_stability_064.py','setup_cache_065.py']]+list((ROOT/'work/translation/en/skills_0.1.71').glob('*.json'))","['build_pot_071.py','pot_fix_071.py','verify_pot_071.py','verify_stability_071.py','setup_pot_build_071.py']]")
 after=after.replace('cache065_arena','pot071_name_cache')
 assert "verify_cache_065.py" not in after and 'pot_fix_071' in after
 target=ROOT/'tools/build_pot_071.py';assert not target.exists()
 print(dict(mode='write' if a.write else 'preview',path=str(target),base='0.1.70',output='0.1.71',changed_lines=sum(x!=y for x,y in zip(before.splitlines(),after.splitlines()))))
 if a.write:target.write_text(after,encoding='utf8')
if __name__=='__main__':main()
