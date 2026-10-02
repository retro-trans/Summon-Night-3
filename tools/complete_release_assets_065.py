"""Preview documentation/checksum assets after both Retro Trans patches verify."""
import argparse,json,hashlib
from sn3_archive import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 out=ROOT/'work/output/release-v0.1.65';m=json.loads((out/'BUILD-MANIFEST.json').read_text());v=json.loads((out/'VALIDATION.json').read_text())
 patches=sorted(p.name for p in out.glob('*.xdelta'));assert patches==['SN3-English-v0.1.55-to-v0.1.65.xdelta','SN3-English-v0.1.65.xdelta']
 files={'README-v0.1.65.txt':(ROOT/'docs/RELEASE_0.1.65.md').read_bytes(),'CHANGELOG-v0.1.65.txt':(ROOT/'CHANGELOG.md').read_bytes()}
 names=sorted(p.name for p in out.iterdir() if p.is_file() and p.name not in {'SHA1SUMS-v0.1.65.txt','SHA256SUMS-v0.1.65.txt'})
 names=sorted(set(names)|set(files))
 def payload(n):return files[n] if n in files else (out/n).read_bytes()
 for algorithm in ('sha1','sha256'):
  files[algorithm.upper()+'SUMS-v0.1.65.txt']=''.join(hashlib.new(algorithm,payload(n)).hexdigest()+'  '+n+'\n' for n in names).encode()
 print(json.dumps(dict(mode='write' if a.write else 'preview',destination=str(out),new_assets=list(files),xdelta_patches=patches),indent=2))
 if a.write:
  for name,data in files.items():
   path=out/name;assert not path.exists();path.write_bytes(data)
if __name__=='__main__':main()
