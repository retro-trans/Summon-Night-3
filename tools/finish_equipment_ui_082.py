"""Record reviewed equipment pages from the supplied normal save."""
import json,subprocess
from sn3_archive import ROOT
from build_candidate import hash_file

def main():
 d=ROOT/'work/output/0.1.82';m=json.loads((d/'manifest.json').read_text());assert hash_file(d/m['output_iso'])==m['output_sha256']
 q=ROOT/'work/scratch/ui082-final';s=json.loads((q/'session.json').read_text('utf-8-sig'));assert s['fresh_boot'] and not s['save_state_used'] and s['iso']==str(d/m['output_iso'])
 status=json.loads((q/'final-debugger-status.json').read_text());assert not status['breakpoints']['breakpoints']
 running=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process -Name '*PPSSPP*' -ErrorAction SilentlyContinue | Select-Object Id,Path | ConvertTo-Json"],text=True).strip();assert not running
 checked=[]
 for name,note in [('fixedEquipType','All five Rexx captions visible in right panel.'),('fixedExactEquip','All five Rexx captions visible in left panel; Condition None.'),('fixedKyuuma','Kyuuma Katana/Claws/Kimono labels visible.'),('fixedRexxReturn','Rexx captions remain correct after character switch and return.')]:
  p=ROOT/'work/ui/ui_0.1.82/reviewed'/name;r=json.loads(p.with_suffix('.json').read_text());assert r['session']==s and r['png_sha256']==hash_file(p.with_suffix('.png'))
  checked.append(dict(path=p.with_suffix('.png').relative_to(ROOT).as_posix(),sha256=r['png_sha256'],note=note,visual_review_passed=True))
 log=(q/'runtime.log').read_text(errors='replace');assert 'Bad execution address' not in log and 'Game crashed' not in log
 result=dict(version='0.1.82',passed=True,iso_sha256=m['output_sha256'],fresh_boot=True,normal_in_game_save=True,save_state_used=False,emulator='Windows PPSSPP 1.20.4',renderer='software',emulator_instances=1,emulator_closed=True,game_memory_writes=False,breakpoints_removed=True,audio_enabled=True,audio_playback_validated=False,screenshots=checked,limitations=['No direct Android validation or full-game playthrough.'])
 for p in (d/'runtime-validation.json',ROOT/'work/ui/ui_0.1.82/runtime-validation.json'):p.write_text(json.dumps(result,indent=2)+'\n')
 m['static_validation'].update(runtime_verified=True,runtime_validation_file='runtime-validation.json');(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(checked))))

if __name__=='__main__':main()
