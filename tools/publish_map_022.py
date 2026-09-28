"""Verify and publish the tested map-VWF candidate. Dry run by default."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 src=(ROOT/'work/scratch/map_candidate_0.1.22').resolve();dest=(ROOT/'work/output/0.1.22').resolve()
 assert ROOT.resolve() in src.parents and ROOT.resolve() in dest.parents and not dest.exists()
 m=json.loads((src/'manifest.json').read_text());qa=ROOT/'work/ui/map_0.1.22/runtime/validation.json';r=json.loads(qa.read_text())
 assert m['version']=='0.1.22' and hash_file(src/m['output_iso'])==m['output_sha256']==r['source_iso_sha256']
 for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 assert m['map022_vwf']['changed_bytes']==3 and r['loaded_hook_verified'] and r['visual_pass']
 additions=[ROOT/'tools'/n for n in ['map_runtime_022.py','publish_map_022.py']]
 additions += [ROOT/'docs/MAP_VWF_0.1.22.md']+list((ROOT/'work/ui/map_0.1.22').rglob('*'))
 for f in additions:
  if f.is_file():m['inputs_sha256'][f.relative_to(ROOT).as_posix()]=hash_file(f)
 m['static_validation']['runtime_verified']=True;m['map022_runtime']=r
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),sha256=m['output_sha256'],bound_inputs=len(m['inputs_sha256'])),indent=2))
 if a.write:
  (src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');src.rename(dest)
if __name__=='__main__':main()
