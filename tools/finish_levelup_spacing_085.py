"""Record clean boot and loaded Level Up literals without changing game RAM."""
import base64,json
from levelup_spacing_085 import ROOT,TEXT,encoded
from options_runtime_078 import client
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.85';m=json.loads((d/'manifest.json').read_text('utf8'));r=m['levelup085_fix'];cfg=json.loads(TEXT.read_text('utf8'))
 s=json.loads((ROOT/'work/scratch/ui085-final/session.json').read_text('utf-8-sig'));assert s['fresh_boot'] and not s['save_state_used'] and s['iso']==str(d/m['output_iso'])
 request=client(19450);assert request('game.status')['game']['id']=='NPJH50380'
 for name in ('confirm','controls','skills'):
  raw=encoded(cfg[name]);actual=base64.b64decode(request('memory.read',address=0x08804000+r[name+'_address'],size=len(raw))['base64']);assert actual==raw
 log=(ROOT/'work/scratch/ui085-final/runtime.log').read_text('utf8',errors='replace');assert all(t not in log for t in ('Bad memory access','NO_MEMORY','out of memory','failed to allocate'))
 checked=[]
 for name in ('room','unitMenu'):
  p=ROOT/'work/ui/ui_0.1.85/reviewed'/name;capture=json.loads(p.with_suffix('.json').read_text('utf8'));assert capture['session']==s and capture['png_sha256']==hash_file(p.with_suffix('.png'))
  checked.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=capture['png_sha256']))
 result=dict(passed=True,version='0.1.85',iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',jit=True,renderer='software',fresh_boot=True,normal_save_loaded=True,save_state_used=False,loaded_literal_groups=3,game_memory_writes=False,screenshots=checked,exact_post_battle_levelup_screen_reproduced=False,limitations=['Available Chapter 16 room save used; post-battle Level Up save unavailable.','Native formatter execution, buffer guards and real glyph metrics verify the reported hint layout; no exact-screen gameplay claim.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/ui_0.1.85/runtime-validation.json'):p.write_text(json.dumps(result,indent=2)+'\n','utf8')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json')
 for name in ('tools/finish_levelup_spacing_085.py','tools/package_test_ui_085.py','tools/launch_ui_085.ps1','tools/ui_runtime_085.py','docs/UI_0.1.85.md'):m['inputs_sha256'][name]=hash_file(ROOT/name)
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n','utf8');print(json.dumps(result),flush=True)

if __name__=='__main__':main()
