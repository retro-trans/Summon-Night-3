"""Verify loaded banner dispatch and record fresh normal-suspend battle QA."""
import base64,json,struct
from sn3_archive import ROOT
from options_runtime_078 import client
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.86';m=json.loads((d/'manifest.json').read_text('utf8'));r=m['banner086_fix'];session=json.loads((ROOT/'work/scratch/ui086-battle/session.json').read_text('utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used'] and session['iso']==str(d/m['output_iso'])
 request=client(19452);assert request('game.status')['game']['id']=='NPJH50380';base=0x08804000
 def target(p):return request('memory.disasm',address=base+p,count=1)['lines'][0]['branch']['targetAddress']
 assert target(r['prior_match'])==base+int(r['code_address'],16)+r['labels']['match']
 expected=base+int(r['code_address'],16)+r['labels']['center_bind'];assert target(r['prior_center_branch'])==expected and target(0x14ebd8)==expected
 log=(ROOT/'work/scratch/ui086-battle/runtime.log').read_text('utf8',errors='replace');assert all(t not in log for t in ('Bad memory access','NO_MEMORY','out of memory','failed to allocate'))
 checked=[]
 for name in ('battle','afterEnemy'):
  p=ROOT/'work/ui/ui_0.1.86/reviewed'/name;capture=json.loads(p.with_suffix('.json').read_text('utf8'));assert capture['session']==session and capture['png_sha256']==hash_file(p.with_suffix('.png'));checked.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=capture['png_sha256']))
 result=dict(passed=True,version='0.1.86',iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',jit=True,renderer='software',fresh_boot=True,normal_suspend_loaded=True,save_state_used=False,battle_continued_without_memory_fault=True,loaded_redirects_verified=3,game_memory_writes=False,exact_reported_skill_replayed=False,natural_matching_banner_observed=False,screenshots=checked,limitations=['Existing recovered normal Suspend save used; supplied scene save is unavailable.','Exact Deadly Strike banner verified through emitted dispatch/widget/pixel tests, not claimed as replayed in the natural battle.','No Android, hardware renderer or full-playthrough claim.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/ui_0.1.86/runtime-validation.json'):p.write_text(json.dumps(result,indent=2)+'\n','utf8',newline='\n')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json')
 for name in ('tools/finish_banner_vwf_086.py','tools/package_test_ui_086.py','tools/launch_ui_086.ps1','tools/ui_runtime_086.py','tools/probe_banner_086.py','docs/UI_0.1.86.md'):m['inputs_sha256'][name]=hash_file(ROOT/name)
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n','utf8');print(json.dumps(result),flush=True)

if __name__=='__main__':main()
