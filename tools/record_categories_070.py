"""Preview and record verified local build evidence; never alter historical builds."""
import argparse,json,copy
from concurrent.futures import ThreadPoolExecutor
from sn3_archive import ROOT,GameSource
from categories_fix_070 import BASE,prepare_elf,prepare_tables
from build_candidate import hash_file

def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/output/0.1.70';ui=ROOT/'work/ui/categories_0.1.70';manifest=json.loads((folder/'manifest.json').read_text())
 audit=json.loads((ui/'cumulative-validation.json').read_text());native=json.loads((ui/'category-validation.json').read_text())
 assert audit['passed'] and native['passed'] and len(audit['checks'])==14
 assert audit['iso_sha256']==manifest['output_sha256']==hash_file(folder/manifest['output_iso'])
 def check(item):n,h=item;assert hash_file(ROOT/n)==h,n
 with ThreadPoolExecutor(max_workers=8) as workers:list(workers.map(check,manifest['inputs_sha256'].items()))
 assert (folder/'EBOOT.elf').read_bytes()==prepare_elf()[0]
 with GameSource(folder/manifest['output_iso']) as candidate,GameSource(BASE/'Summon_Night_3_EN_0.1.69.iso') as prior:
  packs=prepare_tables(prior)[0]
  for n,wanted in packs.items():assert candidate.resource('02.DAT',n)==wanted
 audit['checks'].append(dict(name='Native equipment/transform help, retained stat help and startup notice',passed=True,details=native))
 log=(ROOT/'work/scratch/categories070-runtime/runtime.log').read_text(errors='replace');assert '0.1.70.iso' in log
 assert not any(s in log for s in ('Bad memory access','E[MEMMAP]','Game crashed'))
 cfg=(ROOT/'work/scratch/categories070-runtime/strict.ini').read_text(encoding='utf-8-sig').replace(' ','');assert 'IgnoreBadMemAccess=False' in cfg and 'CPUCore=1' in cfg
 shot=json.loads((ui/'runtime/boot.json').read_text());assert shot['cpu']['pc']==144800668 and shot['cpu']['stepping']
 evidence=[ui/'category-validation.json',ui/'cumulative-validation.json',ui/'notice_native.png']+sorted((ui/'runtime').glob('*'))
 runtime=dict(version='0.1.70',iso_sha256=manifest['output_sha256'],fresh_boot=True,save_state_used=False,emulator='PPSSPP 1.20.4',cpu='JIT',graphics='software',ignore_bad_memory_access=False,startup_notice_visually_verified=True,exact_reported_max_mp_screen_visually_verified=False,limitation='Startup notice verified in game. Common stat and new equipment/transform help verified by native formatter execution; matching reported skill selection not visually confirmed.',evidence=[dict(path=str(x.relative_to(ROOT)).replace('\\','/'),sha256=hash_file(x)) for x in evidence])
 print(json.dumps(dict(mode='write' if a.write else 'preview',iso=manifest['output_iso'],sha256=manifest['output_sha256'],groups=len(audit['checks']),new_native_fragments=12,retained_stat_helps=12,notice_visually_verified=True),indent=2))
 if not a.write:return
 for dest,data in [(folder/'stability-report.json',audit),(folder/'runtime-validation.json',runtime),(ui/'runtime-validation.json',runtime)]:
  assert not dest.exists();dest.write_text(json.dumps(data,indent=2)+'\n')
 manifest['static_validation']['runtime_verified']=True
 manifest['stability_validation']=dict(passed=True,groups=len(audit['checks']),report='stability-report.json',sha256=hash_file(folder/'stability-report.json'))
 manifest['runtime_validation']=dict(passed=True,report='runtime-validation.json',sha256=hash_file(folder/'runtime-validation.json'),startup_notice_verified=True,exact_max_mp_screen_verified=False)
 manifest['inputs_sha256']['tools/record_categories_070.py']=hash_file(ROOT/'tools/record_categories_070.py')
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
