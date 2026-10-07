"""Attach completed validation metadata to this new local build only."""
import json,hashlib
from sn3_archive import ROOT
from build_candidate import hash_file
def main():
 folder=ROOT/'work/output/0.1.73';path=folder/'manifest.json';m=json.loads(path.read_text())
 reports={n:json.loads((folder/n).read_text()) for n in ('stability-report.json','runtime-validation.json','name-cache-validation.json')}
 assert all(r['passed'] for r in reports.values())
 assert reports['runtime-validation.json']['iso_sha256']==reports['stability-report.json']['iso_sha256']==m['output_sha256']
 assert hash_file(folder/m['output_iso'])==m['output_sha256']
 m['static_validation']['runtime_verified']=True
 m['stability_validation']=dict(passed=True,groups=len(reports['stability-report.json']['checks']),report='stability-report.json',sha256=hash_file(folder/'stability-report.json'))
 m['runtime_validation']=dict(passed=True,report='runtime-validation.json',sha256=hash_file(folder/'runtime-validation.json'),exact_white_stone_case_verified=True)
 m['name_cache_validation']=dict(passed=True,cases=1220,report='name-cache-validation.json',sha256=hash_file(folder/'name-cache-validation.json'))
 for name in ('pot_runtime_073.py','record_pot_073.py','finalize_pot_073.py','package_test_pot_073.py','launch_pot_071.ps1'):
  p=ROOT/'tools'/name;m['inputs_sha256']['tools/'+name]=hash_file(p)
 path.write_text(json.dumps(m,indent=2)+'\n')
 print(json.dumps(dict(version='0.1.73',passed=True,groups=m['stability_validation']['groups'],native_cases=1220)))
if __name__=='__main__':main()
