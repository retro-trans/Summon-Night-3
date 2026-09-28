"""Verify the tested candidate and publish it; default is a read-only dry run."""
import argparse,json
from sn3_archive import ROOT
from build_candidate import hash_file

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 src=(ROOT/'work/scratch/descriptions_candidate_0.1.21').resolve();dest=(ROOT/'work/output/0.1.21').resolve()
 assert ROOT.resolve() in src.parents and ROOT.resolve() in dest.parents and not dest.exists()
 m=json.loads((src/'manifest.json').read_text());qa=ROOT/'work/ui/descriptions_0.1.21/runtime/validation.json';r=json.loads(qa.read_text())
 assert m['version']=='0.1.21' and hash_file(src/m['output_iso'])==m['output_sha256']==r['source_iso_sha256']
 for n,h in m['inputs_sha256'].items():assert hash_file(ROOT/n)==h,n
 assert r['resident_table_descriptions_verified']==42 and r['native_formatter_all_records']==235 and r['crash_fix_spans_verified']==5
 assert all(not t['pending'] for t in m['descriptions021_tables']['tables'])
 additions=[ROOT/'tools'/n for n in ['descriptions_runtime_021.py','verify_descriptions_live_021.py','publish_descriptions_021.py']]
 additions += [ROOT/'docs/DESCRIPTIONS_0.1.21.md']+list((ROOT/'work/ui/descriptions_0.1.21').rglob('*'))
 for f in additions:
  if f.is_file():m['inputs_sha256'][f.relative_to(ROOT).as_posix()]=hash_file(f)
 m['static_validation']['runtime_verified']=True;m['descriptions021_runtime']=r
 print(json.dumps(dict(mode='write' if a.write else 'dry-run',destination=str(dest),sha256=m['output_sha256'],bound_inputs=len(m['inputs_sha256']),spell_records=235),indent=2))
 if a.write:
  (src/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');src.rename(dest)
if __name__=='__main__':main()
