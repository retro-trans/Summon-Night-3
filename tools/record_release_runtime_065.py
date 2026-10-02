"""Record the manually inspected fresh-boot smoke-test evidence; preview first."""
import argparse,json,hashlib
from pathlib import Path
from release_preflight import REQUIRED
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args()
 build=ROOT/'work/output/0.1.65';ui=ROOT/'work/ui/release_0.1.65';runtime=ROOT/'work/scratch/release065-runtime'
 m=json.loads((build/'manifest.json').read_text());session=json.loads((runtime/'session.json').read_text('utf-8-sig'))
 assert Path(session['iso']).resolve()==build/m['output_iso'] and session['fresh_boot'] and not session['save_state_used']
 log=(runtime/'runtime.log').read_text('utf8',errors='replace')
 assert '0.1.65.iso' in log and not any(x in log.lower() for x in ('bad memory access','invalid memory','memfault'))
 cfg=(runtime/'strict.ini').read_text('utf-8-sig');assert 'IgnoreBadMemAccess=False' in cfg and 'CPUCore=1' in cfg
 evidence=[]
 for name in ('load_menu_ready','loaded','battle_ready','battle_menu','brave_goals','inventory','black_rose','summon_index','dritol'):
  png=ui/'runtime'/f'{name}.png';meta=png.with_suffix('.json');d=json.loads(meta.read_text())
  assert d['png_sha256']==sha(png) and d['cpu']['pc']==int(d['display_import_address'],16)
  assert d['method']=='software VRAM at sceDisplaySetFrameBuf'
  evidence.extend(dict(path=x.relative_to(ROOT).as_posix(),sha256=sha(x)) for x in (png,meta))
 resident=ui/'resident-table-validation.json';resident_report=json.loads(resident.read_text())
 assert resident_report['passed'] and resident_report['text_pointers_checked']==620
 evidence.append(dict(path=resident.relative_to(ROOT).as_posix(),sha256=sha(resident)))
 passed=('continue_late_battle','brave_goals','equipment','summon_index')
 report=dict(version='0.1.65',iso_sha256=m['output_sha256'],fresh_boot=True,normal_save=True,save_state_used=False,
  emulator='PPSSPP 1.20.4',cpu='JIT',graphics='software',ignore_bad_memory_access=False,
  cases={n:dict(status='passed',scope='Chapter 15 normal-save menu opening/navigation; captures manually inspected. No memory fault.') if n in passed else dict(status='pending',reason='Not exercised in this exact candidate session.') for n in REQUIRED},
  evidence=evidence,no_bad_memory_access_in_log=True,log_sha256=sha(runtime/'runtime.log'),
  notes=['Display-import debugger pauses are intentional screenshot stops, not crashes.','Exact recently reported reward/recruitment, map, casting banner, Level Up and Learn Skills screens still require matching saves.','New individual battle-event paths and their runtime allocations are not exhaustively tested.'])
 print(json.dumps(dict(mode='write' if a.write else 'preview',cases=report['cases'],evidence_files=len(evidence),iso_sha256=report['iso_sha256']),indent=2))
 if a.write:
  for folder in (build,ui):(folder/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n')
  (ui/'stability-report.json').write_bytes((build/'stability-report.json').read_bytes())
if __name__=='__main__':main()
