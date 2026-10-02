"""Preview and stage only release-related source/evidence; reject secrets."""
import argparse,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GIT=['git','-c','safe.directory='+ROOT.as_posix()]
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 manifest=json.loads((ROOT/'work/output/0.1.64/manifest.json').read_text());paths={n for n in manifest['inputs_sha256'] if not n.startswith('work/output/')}
 paths|={p.relative_to(ROOT).as_posix() for p in (ROOT/'tools').iterdir() if re.search(r'_(?:05[6-9]|06[0-4])\.(?:py|ps1)$',p.name)}
 paths|={p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').iterdir() if re.search(r'0\.1\.(?:5[6-9]|6[0-4])\.md$',p.name)}
 paths|={p.relative_to(ROOT).as_posix() for p in (ROOT/'work/ui/release_0.1.64').rglob('*') if p.is_file() and p.suffix in ('.png','.json')}
 paths.add('CHANGELOG.md')
 for name in sorted(paths):
  path=ROOT/name;assert path.is_file(),name
  assert path.suffix not in ('.iso','.elf','.bin','.xdelta','.ppst','.sav','.pem','.key'),name
  if path.suffix in ('.py','.ps1','.json','.md'):
   text=path.read_text(encoding='utf-8-sig')
   assert not any(s in text for s in ('-----BEGIN PRIVATE KEY-----','"private_key":','"refresh_token":')),name
   assert sum('\u3040'<=c<='\u9fff' for c in text)<10000,('Extensive source text',name)
 staged=subprocess.check_output(GIT+['diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines();assert all(n in paths for n in staged),('Unrelated staged changes',staged)
 untracked=set(subprocess.check_output(GIT+['ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines());modified=set(subprocess.check_output(GIT+['diff','--name-only'],cwd=ROOT,text=True).splitlines())
 selected=sorted(paths&(untracked|modified|set(staged)))
 print(json.dumps(dict(mode='stage' if a.write else 'preview',files=selected),indent=2),flush=True)
 if a.write:subprocess.run(GIT+['add','--']+selected,cwd=ROOT,check=True)
if __name__=='__main__':main()
