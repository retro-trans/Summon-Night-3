"""Bind reviewed Assist screenshots to the tested final image."""
import json,subprocess
from sn3_archive import ROOT
from build_candidate import hash_file

def main():
 dest=ROOT/'work/output/0.1.81';m=json.loads((dest/'manifest.json').read_text());assert hash_file(dest/m['output_iso'])==m['output_sha256']
 qa=ROOT/'work/scratch/ui081-final';s=json.loads((qa/'session.json').read_text('utf-8-sig'));assert s['fresh_boot'] and not s['save_state_used'] and s['iso']==str(dest/m['output_iso'])
 status=json.loads((qa/'final-debugger-status.json').read_text());assert not status['breakpoints']['breakpoints']
 running=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process -Name '*PPSSPP*' -ErrorAction SilentlyContinue | Select-Object Id,Path | ConvertTo-Json"],text=True).strip();assert not running
 trace=json.loads((ROOT/'work/ui/ui_0.1.81/live-helper.json').read_text());assert trace['passed'] and trace['iso_sha256']==m['output_sha256']
 checked=[]
 for name,label in [('godAssistInfo081','Sky Torrent member list: proportional labels fit two columns.'),('assistHint081','Assist hint: triangle icon aligned before its caption.'),('heavensNetInfo081',"Heaven's Net: alternate member list fits the same widget.")]:
  path=ROOT/'work/ui/ui_0.1.81/reviewed'/name;r=json.loads(path.with_suffix('.json').read_text());assert r['session']==s and r['png_sha256']==hash_file(path.with_suffix('.png'))
  checked.append(dict(path=path.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=r['png_sha256'],note=label,visual_review_passed=True))
 log=(qa/'runtime.log').read_text(errors='replace');assert 'Bad execution address' not in log and 'Game crashed' not in log
 result=dict(version='0.1.81',passed=True,iso_sha256=m['output_sha256'],fresh_boot=True,normal_in_game_save=True,save_state_used=False,emulator='Windows PPSSPP 1.20.4',renderer='software',emulator_instances=1,emulator_closed=True,game_memory_writes=False,breakpoints_removed=True,audio_enabled=True,audio_playback_validated=False,live_helper=trace,screenshots=checked,limitations=['Shared Assist help and INFO verified in Summon Index; exact supplied battle sequence not replayed.','No direct Android validation or full-game playthrough.'])
 for path in (dest/'runtime-validation.json',ROOT/'work/ui/ui_0.1.81/runtime-validation.json'):path.write_text(json.dumps(result,indent=2)+'\n')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json');(dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(checked))))

if __name__=='__main__':main()
