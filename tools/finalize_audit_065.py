"""Preview then append arena and Learn Skills checks to the recorded audit."""
import argparse,json,hashlib
from sn3_archive import ROOT,GameSource
import cache_065,verify_cache_065,verify_skills_064
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/output/0.1.65';target=folder/'stability-report.json';r=json.loads(target.read_text());assert r['passed']
 elf=(folder/'EBOOT.elf').read_bytes();assert elf==cache_065.prepare_elf()[0]
 verify_skills_064.prepare_elf=cache_065.prepare_elf
 with GameSource(folder/'Summon_Night_3_EN_0.1.65.iso') as src:
  skills=verify_skills_064.verify(elf,src.resource('02.DAT',3))
 skills['executable_unchanged']=False;skills['only_new_executable_change']='private chapter-common script arena'
 checks=[dict(name='Private chapter script arena and relocation',passed=True,details=verify_cache_065.verify()),dict(name='Four reported Learn Skills names and help blocks',passed=True,details=skills)]
 assert not any(c['name'] in {n['name'] for n in checks} for c in r['checks'])
 print(json.dumps(dict(mode='write' if a.write else 'preview',existing_groups=len(r['checks']),new_groups=[c['name'] for c in checks],arena_cases=checks[0]['details']['abi_cases'],skills=len(skills['skills'])),indent=2))
 if a.write:
  r['checks'].extend(checks)
  r['validation_inputs_sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('tools/verify_stability_065.py','tools/finalize_audit_065.py','tools/verify_cache_065.py')}
  target.write_text(json.dumps(r,indent=2)+'\n');(folder/'ui-regression.json').write_text(json.dumps(skills,indent=2)+'\n')
if __name__=='__main__':main()
