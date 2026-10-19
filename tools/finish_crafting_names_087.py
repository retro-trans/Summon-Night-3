"""Record normal-save accessory rendering and finalize the local test inputs."""
import json
from sn3_archive import ROOT
from options_runtime_078 import client
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.87';m=json.loads((d/'manifest.json').read_text('utf8'))
 qa=ROOT/'work/scratch/ui087-candidate';session=json.loads((qa/'session.json').read_text('utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used'] and session['iso']==str(d/m['output_iso'])
 request=client(19454);assert request('game.status')['game']['id']=='NPJH50380'
 log=(qa/'runtime.log').read_text('utf8',errors='replace')
 assert all(t not in log for t in ('Bad memory access','NO_MEMORY','out of memory','failed to allocate'))
 screenshots=[]
 for name in ('loaded','accessories'):
  p=ROOT/'work/ui/ui_0.1.87/reviewed'/name;capture=json.loads(p.with_suffix('.json').read_text('utf8'))
  assert capture['session']==session and capture['png_sha256']==hash_file(p.with_suffix('.png'))
  screenshots.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=capture['png_sha256']))
 r=dict(passed=True,version='0.1.87',iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',renderer='software',jit=True,
  fresh_boot=True,normal_save_loaded=True,save_state_used=False,accessory_inventory_opened=True,
  corrected_name_seen='1-Eye Magatama',game_memory_writes=False,screenshots=screenshots,
  limitations=['Corrected accessory name visually checked in normal inventory; exact battle crafting scene not replayed.',
   'All 85 nonempty accessory names checked against the narrower crafting column through encoded proportional font metrics.',
   'No Android, hardware-renderer or full-playthrough claim.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/ui_0.1.87/runtime-validation.json'):
  p.write_text(json.dumps(r,indent=2)+'\n','utf8',newline='\n')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json')
 for name in ('tools/finish_crafting_names_087.py','tools/launch_ui_087.ps1','tools/ui_runtime_087.py','tools/package_test_ui_087.py','docs/UI_0.1.87.md'):
  m['inputs_sha256'][name]=hash_file(ROOT/name)
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n','utf8',newline='\n');print(json.dumps(r),flush=True)

if __name__=='__main__':main()
