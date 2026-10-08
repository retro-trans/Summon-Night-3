"""Record manually reviewed fresh-save screenshots for the final 080 image."""
import json,hashlib,subprocess
from sn3_archive import ROOT
from build_candidate import hash_file

CASES={
 'completeVwfPopup':'Max-level popup: English prefix and proportional spacing',
 'completeThrow':'Sonolar proficiency: bounded help, no error or duplicate mastery',
 'completeWill':'Will skill cards: P. Barrier restored alongside translated labels',
 'completeAlieze':'Alieze skill cards: Sum. Mastery restored after character cycling',
 'completeReplayCatalog':'Replay selection help and chapter labels translated',
 'completeReplayAzlier':'Chapter 7 Azlier condition fits its strip and complete help displays',
}

def main():
 dest=ROOT/'work/output/0.1.80';m=json.loads((dest/'manifest.json').read_text());iso=dest/m['output_iso'];assert hash_file(iso)==m['output_sha256']
 qa=ROOT/'work/scratch/ui080-complete';session=json.loads((qa/'session.json').read_text('utf-8-sig'));assert session['fresh_boot'] and not session['save_state_used']
 assert session['iso']==str(iso) and session['port']==19444
 live=json.loads((qa/'final-debugger-status.json').read_text());assert not live['breakpoints']['breakpoints']
 running=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process -Name '*PPSSPP*' -ErrorAction SilentlyContinue | Select-Object Id,Path | ConvertTo-Json"],text=True).strip();assert not running,running
 reviewed=[]
 for name,label in CASES.items():
  p=ROOT/'work/ui/ui_0.1.80/reviewed'/name;report=json.loads(p.with_suffix('.json').read_text());assert report['session']==session
  assert hash_file(p.with_suffix('.png'))==report['png_sha256']
  reviewed.append(dict(label=label,screenshot=p.with_suffix('.png').relative_to(ROOT).as_posix(),png_sha256=report['png_sha256'],capture_report_sha256=hash_file(p.with_suffix('.json')),visual_review_passed=True))
 log=(qa/'runtime.log').read_text(errors='replace');assert 'Bad execution address' not in log and 'Game crashed' not in log
 result=dict(version='0.1.80',passed=True,iso_sha256=m['output_sha256'],emulator='Windows PPSSPP 1.20.4',renderer='software',cpu='JIT',fresh_boot=True,normal_save_loaded=True,save_state_used=False,game_memory_writes=False,capture_breakpoints_removed=True,emulator_instances=1,emulator_closed_after_validation=True,audio_enabled=True,audio_playback_validated=False,reviewed_cases=reviewed,static_checks=json.loads((dest/'asset-validation.json').read_text()),limitations=['Exact Dritol summon-popup and Nagare battle-event paths were verified by executing the relocated name mapper, not replayed live.','No direct Android validation or full-game playthrough.'])
 (dest/'runtime-validation.json').write_text(json.dumps(result,indent=2)+'\n');m['static_validation']['runtime_verified']=True;m['static_validation']['runtime_validation_file']='runtime-validation.json';(dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (ROOT/'work/ui/ui_0.1.80/runtime-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(reviewed),iso_sha256=m['output_sha256'])))

if __name__=='__main__':main()
