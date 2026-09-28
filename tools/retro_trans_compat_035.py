"""Test existing release bytes with Retro Trans; prepare canonical metadata.

Preview by default. --write executes the actual manual and catalog patch paths
using the patcher's bundled engine. Catalog network I/O is represented by the
already downloaded release asset while this game's repository is private.
"""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'work/output/release-v0.1.35'
OUT=ROOT/'work/output/retro-trans-v0.1.35'
SCRATCH=ROOT/'work/scratch/retro-trans-test035'
REPO='retro-trans/Summon-Night-3';TAG='v0.1.35'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--patcher',type=Path,default=ROOT/'work/scratch/retro-trans-tools-compat');a=ap.parse_args()
 sys.path.insert(0,str(a.patcher.resolve()))
 from retro_trans import __version__
 from retro_trans.core import manual_patch,sha256_file,PatchError
 from retro_trans.catalog import Catalog,recognize
 from retro_trans.catalog_builder import release_record
 from retro_trans.release import validate_directory
 old=json.loads((OLD/'BUILD-MANIFEST-v0.1.35.json').read_text());p=old['patches'][0]
 source=ROOT/'work/source/original.iso';delta=OLD/p['patch']
 assert sha256_file(delta)==p['patch_sha256'] and delta.stat().st_size==p['patch_bytes']
 commit=subprocess.check_output(['git','-c','safe.directory='+ROOT.as_posix(),'rev-parse',TAG+'^{}'],text=True).strip()
 patcher_commit=subprocess.check_output(['git','-C',str(a.patcher),'rev-parse','HEAD'],text=True).strip()
 fields={k:v for k,v in p.items() if k in ['patch','source_sha256','source_sha1','source_bytes','target_sha256','target_sha1','target_bytes','patch_sha256','patch_bytes']}
 fields.update(edition='Japanese NPJH50380',language='en',source_version='original',source_format='iso',target_format='iso')
 manifest=dict(schema_version=1,game_id='summon-night-3',game_name='Summon Night 3',platform='PSP',version='0.1.35',source_commit=commit,patches=[fields])
 print(json.dumps(dict(mode='execute' if a.write else 'preview',retro_trans=__version__,patcher_commit=patcher_commit,manifest=manifest,output=str(OUT),tests=['manual_patch with bundled engine','canonical release validator','catalog release import','source recognition','Latest/Next/explicit route','apply_plan with verified local release asset','target recognition','existing-output rejection'],network_catalog_test=False),indent=2),flush=True)
 if not a.write:return
 assert not OUT.exists() and not SCRATCH.exists()
 SCRATCH.mkdir();OUT.mkdir()
 digest=manual_patch(source,delta,SCRATCH/'manual.iso',cache=SCRATCH/'cache')
 assert digest==p['target_sha256'] and (SCRATCH/'manual.iso').stat().st_size==p['target_bytes']
 print('Actual Retro Trans manual patch: PASS',flush=True)
 shutil.copyfile(delta,OUT/p['patch'])
 (OUT/'BUILD-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
 validation=dict(schema_version=1,manifest_sha256=sha256_file(OUT/'BUILD-MANIFEST.json'),patches=[dict(patch=p['patch'],roundtrip_verified=True,target_sha256=digest)])
 (OUT/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf8')
 protocol=[p['patch'],'BUILD-MANIFEST.json','VALIDATION.json']
 (OUT/'SHA256SUMS.txt').write_text(''.join(sha256_file(OUT/n)+'  '+n+'\n' for n in sorted(protocol)),encoding='ascii')
 validate_directory(OUT)
 base=f'https://github.com/{REPO}/releases/download/{TAG}/'
 class LocalAssets:
  def read(self,url,*args):
   assert url.startswith(base);return (OUT/url[len(base):]).read_bytes()
  def download(self,asset,cache,*args):
   path=OUT/asset.name
   assert asset.url==base+asset.name and path.stat().st_size==asset.size and sha256_file(path)==asset.sha256
   return path
 release=dict(tag_name=TAG,assets=[dict(name=n,size=(OUT/n).stat().st_size,digest='sha256:'+sha256_file(OUT/n),browser_download_url=base+n) for n in protocol+['SHA256SUMS.txt']])
 record=release_record(REPO,release,LocalAssets());catalog=Catalog(dict(schema_version=1,releases=[record]))
 original=recognize(source,catalog);assert len(original)==1 and original[0].version=='original'
 for choice in ['Latest','Next version only','0.1.35']:
  plan=catalog.plan(original[0],choice);assert len(plan.edges)==1 and plan.target.version=='0.1.35'
 from retro_trans.catalog import apply_plan
 result=apply_plan(source,SCRATCH/'automatic.iso',plan,catalog,client=LocalAssets(),cache=SCRATCH/'cache')
 assert sha256_file(result)==digest
 identified=recognize(result,catalog);assert len(identified)==1 and identified[0].version=='0.1.35'
 assert not catalog.plan(identified[0]).edges
 try:manual_patch(source,delta,result,cache=SCRATCH/'cache')
 except PatchError as exc:assert 'already exists' in str(exc)
 else:raise AssertionError('Existing output was not rejected')
 assert sha256_file(source)==p['source_sha256'] and sha256_file(delta)==p['patch_sha256']
 report=dict(retro_trans_version=__version__,patcher_commit=patcher_commit,source_commit=commit,source_sha256=p['source_sha256'],target_sha256=digest,patch_sha256=p['patch_sha256'],manual_patch=True,catalog_validation=True,catalog_recognition=True,catalog_routes=['Latest','Next version only','0.1.35'],catalog_apply=True,target_recognition=True,existing_output_rejected=True,source_preserved=True,network_catalog_discovery=False,reason='Repository private and release prerelease at test time; staged assets supplied locally for catalog application. No visible GUI or CHD test.')
 (SCRATCH/'compatibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
