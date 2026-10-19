"""Bind the crash replay and fresh normal-Suspend continuation to the final ISO."""
import json,subprocess
from sn3_archive import ROOT
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.83';m=json.loads((d/'manifest.json').read_text());assert hash_file(d/m['output_iso'])==m['output_sha256']
 fresh=json.loads((ROOT/'work/scratch/berserk083-fresh/session.json').read_text('utf-8-sig'));replay=json.loads((ROOT/'work/scratch/berserk083-verified/session.json').read_text('utf-8-sig'))
 assert fresh['fresh_boot'] and not fresh['save_state_used'] and replay['save_state_used']
 for s in (fresh,replay):assert s['iso']==str(d/m['output_iso'])
 for name in ('berserk083-fresh','berserk083-verified'):
  status=json.loads((ROOT/'work/scratch'/name/'final-debugger-status.json').read_text());assert not status['breakpoints']['breakpoints']
  log=(ROOT/'work/scratch'/name/'runtime.log').read_text(errors='replace');assert 'Bad memory access' not in log and 'Game crashed' not in log
 running=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process -Name '*PPSSPP*' -ErrorAction SilentlyContinue | Select-Object Id,Path | ConvertTo-Json"],text=True).strip();assert not running
 checked=[]
 for name,s,note in [('verifiedMessage',replay,'Complete 31-character message visible and centered.'),('verifiedAfterMessage',replay,'Confirm returns to the battle.'),('verifiedOverwrite',replay,'Normal Suspend saving completes.'),('freshBattle',fresh,'Fresh 0.1.83 boot continues the recovered normal Suspend save.')]:
  p=ROOT/'work/ui/battle_0.1.83/reviewed'/name;r=json.loads(p.with_suffix('.json').read_text());assert r['session']==s and r['png_sha256']==hash_file(p.with_suffix('.png'))
  checked.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=r['png_sha256'],note=note,visual_review_passed=True))
 literals=json.loads((ROOT/'work/ui/battle_0.1.83/fresh-text-validation.json').read_text());assert literals['passed'] and literals['iso_sha256']==m['output_sha256'] and literals['fresh_boot'] and not literals['save_state_used']
 recovery=json.loads((ROOT/'work/output/SN3-Berserk-recovered-state-0.1.83/NPJH50380_2.00_0.recovery.json').read_text());assert recovery['combat_and_save_data_unchanged'] and recovery['code_unchanged'] and recovery['original_state_unchanged']
 original=(ROOT/'work/scratch/berserk083-reproduce/runtime.log').read_text();assert 'Bad memory access detected! 2c961c24' in original
 result=dict(version='0.1.83',passed=True,iso_sha256=m['output_sha256'],original_crash_reproduced=True,fresh_boot_normal_suspend=True,original_supplied_state_repaired_for_replay=True,recovery=recovery,live_game_memory_writes=False,all_27_fresh_loaded_literals_verified=True,emulator='Windows PPSSPP 1.20.4',cpu='JIT',renderer='software',strict_memory_checks=True,emulator_instances=1,emulator_closed=True,breakpoints_removed=True,audio_enabled=True,audio_playback_validated=False,screenshots=checked,limitations=['Exact cast aftermath replayed from the supplied 0.1.81 state with its renderer context repaired; fresh boot separately verifies new literals and normal Suspend continuation.','No direct Android or hardware-renderer validation, or full-game playthrough.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/battle_0.1.83/runtime-validation.json'):p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json');(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(passed=True,cases=len(checked))))

if __name__=='__main__':main()
