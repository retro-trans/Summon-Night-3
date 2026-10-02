"""Preview release notes and public-catalog verifier before creating files."""
import argparse,json
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 m=json.loads((ROOT/'work/output/0.1.65/manifest.json').read_text());files={}
 original=(ROOT/'docs/RELEASE_0.1.64.md').read_text()
 head,withheld,body=original.split('\n\n',2);assert 'Withheld candidate' in withheld
 b=(head+'\n\n'+body).replace('0.1.64','0.1.65')
 b=b.replace('0.1.56 through 0.1.65.','0.1.56 through 0.1.64, plus the 0.1.65 memory fix.')
 b=b.replace('## Changes since v0.1.55','## Changes since v0.1.55\n\n- Fix a reproduced Chapter 15 Battle Info crash: the chapter-common script\n  now uses a separate loader-owned buffer, preventing it from overwriting\n  the expanded Extra Brave Goal table. All 20 chapter scripts fit the buffer.')
 b=b.replace('all 14 cumulative regression groups','all 16 cumulative regression groups')
 b=b.replace('Fresh-boot PPSSPP checks and their screenshots are recorded separately in','Fresh-boot PPSSPP 1.20.4 checks cover Continue from a Chapter 15 in-game save,\nExtra Brave Goals, equipment Inventory and Summon Index. Screenshots are in')
 b=b.replace('Exact reward/recruitment,','A long Extra Brave Goal list label still clips at its edge.\nExact reward/recruitment,')
 files['docs/RELEASE_0.1.65.md']=b
 b=(ROOT/'tools/verify_retro_trans_live_064.py').read_text().replace('0.1.64','0.1.65').replace('live064','live065').replace('a1732872533cbadaa01f7c117fbddb012e31f0b7de5c7b03733a74d4990dcbe3',m['output_sha256']).replace('1680031744',str(m['output_size_bytes']))
 files['tools/verify_retro_trans_live_065.py']=b
 for n,b in files.items():
  print(('WRITE ' if a.write else 'PREVIEW ')+n+'\n'+b[:550])
  if a.write:
   path=ROOT/n;assert not path.exists();path.write_text(b,encoding='utf8')
if __name__=='__main__':main()
