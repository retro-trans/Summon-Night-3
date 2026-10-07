"""Preview and record final local-build validation and evidence."""
import argparse,json,copy
from concurrent.futures import ThreadPoolExecutor
from sn3_archive import ROOT,GameSource
from categories_fix_068 import prepare_elf,prepare_tables
from build_candidate import hash_file
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 folder=ROOT/'work/output/0.1.68';ui=ROOT/'work/ui/categories_0.1.68';manifest=json.loads((folder/'manifest.json').read_text());audit=json.loads((ui/'cumulative-validation.json').read_text());native=json.loads((ui/'category-validation.json').read_text());status=json.loads((ui/'status-validation.json').read_text())
 assert audit['passed'] and native['passed'] and status['status']['passed'] and status['food_chain']['passed']
 assert len(audit['checks'])==14 and native['table_entries']==613
 assert audit['iso_sha256']==manifest['output_sha256']==hash_file(folder/manifest['output_iso'])
 def check(item):n,h=item;assert hash_file(ROOT/n)==h,n
 with ThreadPoolExecutor(max_workers=8) as workers:list(workers.map(check,manifest['inputs_sha256'].items()))
 assert (folder/'EBOOT.elf').read_bytes()==prepare_elf()[0]
 with GameSource(folder/manifest['output_iso']) as candidate,GameSource(ROOT/'work/output/0.1.67/Summon_Night_3_EN_0.1.67.iso') as prior:
  assert candidate.resource('02.DAT',3)==prepare_tables(prior)[0][3]
 audit['checks'] += [dict(name='Related category translations and native help/master',passed=True,details=native),dict(name='Retained Status and SELECT/Give Food handlers',passed=True,details=status)]
 log=(ROOT/'work/scratch/categories068-runtime/runtime.log').read_text(errors='replace');assert '0.1.68.iso' in log
 assert not any(s in log for s in ('Bad memory access','E[MEMMAP]','Game crashed'))
 cfg=(ROOT/'work/scratch/categories068-runtime/strict.ini').read_text(encoding='utf-8-sig').replace(' ','');assert 'IgnoreBadMemAccess=False' in cfg and 'CPUCore=1' in cfg
 for n in ('battlefield','battlemenu','summonindex','spiritprofiles'):
  r=json.loads((ui/'runtime'/f'{n}.json').read_text());assert r['cpu']['pc']==144800668 and r['cpu']['stepping']
 evidence=[ui/'category-validation.json',ui/'cumulative-validation.json',ui/'status-validation.json',ui/'layout.json']+sorted((ui/'runtime').glob('*'))
 runtime=dict(version='0.1.68',iso_sha256=manifest['output_sha256'],fresh_boot=True,normal_save=True,save_state_used=False,emulator='PPSSPP 1.20.4',cpu='JIT',graphics='software',ignore_bad_memory_access=False,continue_to_chapter15=True,battle_menu=True,summon_index=True,picolit_two_lines_visually_verified=True,exact_map_deployment_skills_verified=False,limitation='The available save is Chapter 15 battle. Matching early-story map, deployment, Learn Skills and casting states remain untested.',evidence=[dict(path=str(x.relative_to(ROOT)).replace('\\','/'),sha256=hash_file(x)) for x in evidence])
 print(json.dumps(dict(mode='write' if a.write else 'preview',iso=manifest['output_iso'],sha256=manifest['output_sha256'],groups=len(audit['checks']),translated_fields=601,translated_map_names=24,reformatted_fields=12,picolit_visual_verified=True),indent=2))
 if not a.write:return
 for dest,data in [(folder/'stability-report.json',audit),(folder/'runtime-validation.json',runtime),(ui/'runtime-validation.json',runtime)]:
  assert not dest.exists();dest.write_text(json.dumps(data,indent=2)+'\n')
 manifest['static_validation']['runtime_verified']=True
 manifest['stability_validation']=dict(passed=True,groups=len(audit['checks']),report='stability-report.json',sha256=hash_file(folder/'stability-report.json'))
 manifest['runtime_validation']=dict(passed=True,report='runtime-validation.json',sha256=hash_file(folder/'runtime-validation.json'),picolit_verified=True,exact_map_deployment_skills_verified=False)
 for path in [ROOT/'tools/record_categories_068.py',ROOT/'tools/categories_runtime_068.py',ROOT/'tools/launch_categories_068.ps1',ROOT/'work/glossary/categories_0.1.68.json']:
  manifest['inputs_sha256'][str(path.relative_to(ROOT)).replace('\\','/')]=hash_file(path)
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
