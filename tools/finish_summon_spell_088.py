"""Record fresh-boot spell-row comparison and finalize local test inputs."""
import json
from sn3_archive import ROOT
from options_runtime_078 import client
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.88';m=json.loads((d/'manifest.json').read_text('utf8'))
 qa=ROOT/'work/scratch/ui088-candidate';session=json.loads((qa/'session.json').read_text('utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used'] and session['iso']==str(d/m['output_iso'])
 assert client(19456)('game.status')['game']['id']=='NPJH50380'
 log=(qa/'runtime.log').read_text('utf8',errors='replace')
 assert all(t not in log for t in ('Bad memory access','NO_MEMORY','out of memory','failed to allocate'))
 screenshots=[]
 for name,version in [('indexlast','0.1.87'),('loaded','0.1.88'),('shine_saber','0.1.88'),('next_summon','0.1.88'),('shine_saber_reopen','0.1.88')]:
  p=ROOT/'work/ui/ui_0.1.88/reviewed'/name;capture=json.loads(p.with_suffix('.json').read_text('utf8'))
  assert capture['session']['fresh_boot'] and not capture['session']['save_state_used']
  assert version in capture['session']['iso'] and capture['png_sha256']==hash_file(p.with_suffix('.png'))
  screenshots.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),version=version,sha256=capture['png_sha256']))
 cache=json.loads((ROOT/'work/ui/ui_0.1.88/runtime-cache.json').read_text('utf8'));assert cache['max_capacity']==16
 native=json.loads((ROOT/'work/ui/ui_0.1.88/native-cache-validation.json').read_text('utf8'));assert native['passed'] and native['iso_sha256']==m['output_sha256']
 r=dict(passed=True,version='0.1.88',iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',renderer='software',jit=True,
  fresh_boot=True,normal_save_loaded=True,save_state_used=False,prior_blank_row_reproduced=True,
  corrected_name_seen='Crush! L.G.Sword',proportional_spacing_observed=True,adjacent_summon_checked='Dark Bringer / Dark Sword',
  corrected_name_survives_page_change=True,runtime_font_cache=cache,native_cache_validation=native,game_memory_writes=False,screenshots=screenshots,
  limitations=['Exact Create Summons casting screen not replayed; the same Shine Saber spell row was compared in Summon Index.',
   'No Android, hardware-renderer or full-playthrough claim.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/ui_0.1.88/runtime-validation.json'):
  p.write_text(json.dumps(r,indent=2)+'\n','utf8',newline='\n')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json')
 for name in ('tools/verify_summon_spell_088.py','tools/finish_summon_spell_088.py','tools/launch_ui_088.ps1','tools/ui_runtime_088.py','tools/package_test_ui_088.py','docs/UI_0.1.88.md'):
  m['inputs_sha256'][name]=hash_file(ROOT/name)
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n','utf8',newline='\n');print(json.dumps(r),flush=True)

if __name__=='__main__':main()
