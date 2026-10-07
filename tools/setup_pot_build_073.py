"""Create the immutable-input save-load repair builder."""
import argparse
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 before=(ROOT/'tools/build_pot_072.py').read_text()
 after=before.replace('0.1.72','0.1.73').replace('0.1.71','0.1.72').replace('_072','_073').replace('pot072_name_cache','pot073_name_cache')
 target=ROOT/'tools/build_pot_073.py';assert not target.exists()
 print(dict(mode='write' if a.write else 'preview',base='0.1.72',output='0.1.73'))
 if a.write:target.write_text(after,encoding='utf8')
if __name__=='__main__':main()
