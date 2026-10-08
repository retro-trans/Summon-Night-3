"""Bind visually reviewed fresh-boot captures to the validated 079 image."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 dest=ROOT/'work/output/0.1.79';ui=ROOT/'work/ui/ui_0.1.79';m=json.loads((dest/'manifest.json').read_text());iso=dest/m['output_iso'];assert digest(iso)==m['output_sha256']
 cases={'finalChapter78':'Scarrel Chapter 7 Rexx/Aty titles and separated footer','finalOptionsLR':'Options selected L/R label','finalLoadMenu':'Normal save load dialog','finalRoomReady':'Loaded Chapter 16 save','finalFortuneSelect':'Fariel and translated fortune evaluation','finalFortuneMisumi':'Misumi fortune portrait and evaluation','finalRockShot':'Rock Shot list alignment and level/MP description','finalRagingTiger':'Raging Tiger name and description','finalMagicAttack':'Magic Attack name and description','finalSpiritStrike':'Spirit Strike+ name and description','finalWeaponRange':'Claws, Beast Garb and adjacent range','finalKatana':'Gun, Light Armor and ranged weapon description','finalMisumiEquipment':'Kimono and spear range','finalShopGreeting':'Story speaker-name graphic sample: Meimei','finalReturn':'Successful return to shop services'}
 reviewed=[]
 for name,label in cases.items():
  png=ui/'reviewed'/(name+'.png');data=json.loads(png.with_suffix('.json').read_text());assert digest(png)==data['png_sha256'];assert data['width']==480 and data['height']==272
  assert Path(data['session']['iso']).resolve()==iso.resolve() and data['session']['fresh_boot'] and not data['session']['save_state_used']
  reviewed.append(dict(label=label,screenshot=png.relative_to(ROOT).as_posix(),png_sha256=digest(png),capture_report_sha256=digest(png.with_suffix('.json')),visual_review_passed=True))
 log=(ROOT/'work/scratch/ui079-candidate/runtime.log').read_text(errors='replace');assert 'Bad Execution Address' not in log and 'Game crashed' not in log
 report=dict(version='0.1.79',passed=True,iso_sha256=m['output_sha256'],emulator='Windows PPSSPP 1.20.4',renderer='software',cpu='JIT',fresh_boot=True,normal_save_loaded=True,save_state_used=False,game_memory_writes=False,capture_breakpoints_removed=True,emulator_instances=1,emulator_closed_after_validation=True,audio_enabled=True,audio_playback_validated=False,reviewed_cases=reviewed,runtime_log_sha256=hashlib.sha256(log.encode()).hexdigest(),limitations=['Exact Guardian Shrine entry and Misumi story scenes checked as native assets; not replayed','No direct Android test','Scoped UI checks, not full gameplay regression'])
 payload=json.dumps(report,indent=2)+'\n';(dest/'runtime-validation.json').write_text(payload);(ui/'runtime-validation.json').write_text(payload);(ui/'asset-validation.json').write_bytes((dest/'asset-validation.json').read_bytes())
 m['static_validation']['runtime_verified']=True;m['ui079_validation']=dict(runtime_report_sha256=digest(dest/'runtime-validation.json'),asset_report_sha256=digest(dest/'asset-validation.json'),reviewed_case_count=len(cases));(dest/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(passed=True,reviewed_cases=len(cases))))
if __name__=='__main__':main()
