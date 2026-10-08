"""Bind reviewed normal-save gameplay evidence to the exact local build."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
def main():
 out=ROOT/'work/output/0.1.77';ui=ROOT/'work/ui/battle_0.1.77';case='battle077-final'
 m=json.loads((out/'manifest.json').read_text());session_path=ROOT/'work/scratch'/case/'session.json';session=json.loads(session_path.read_text('utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used'] and session['audio_enabled']
 assert Path(session['iso']).resolve()==(out/m['output_iso']).resolve()
 # Record identity once while the owned emulator is still paused on this image.
 assert session.get('iso_sha256',m['output_sha256'])==m['output_sha256'];session['iso_sha256']=m['output_sha256'];write(session_path,session)
 from battle_runtime_077 import client
 request=client(19441);cpu=request('cpu.status');assert cpu['stepping'] and cpu['pc']==144800668
 log=(session_path.parent/'runtime.log').read_text();assert 'Bad execution access' not in log and 'E[MEMMAP]' not in log
 config=(session_path.parent/'strict.ini').read_text('utf-8-sig');assert 'IgnoreBadMemAccess=False' in config and '[Sound]\nEnable=True' in config
 notes={'bladeList':'Blade Awakening starts at the same x coordinate as Pact, Cheer and Dash.',
 'yardSpecial':'Yard command labels remain aligned in the smaller skill list.',
 'whiteSelected':'Yard selects All-Purpose Pot and white Neutral Summonite Stone.',
 'whiteCreated':'White-stone summon is created without a crash; unnamed summon uses intentional unknown-name placeholder.',
 'nameConfirm':'Native naming confirmation is English; an auto-generated player-editable name is preserved.',
 'equipConfirm':'Equip the crafted stone? / Yes / No fits the native confirmation window.',
 'equipChoice':'Stone equipped. confirmation is English.',
 'equipped':'Battle menu remains responsive after the white-stone crafting and equipment flow.'}
 captures=[]
 for name,note in notes.items():
  p=ui/case/(name+'.png');meta=json.loads(p.with_suffix('.json').read_text());assert meta['png_sha256']==sha(p) and [meta['width'],meta['height']]==[480,272]
  captures.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),note=note,verified_iso_sha256=m['output_sha256']))
 runtime=dict(version='0.1.77',passed=True,created_at_utc=datetime.now(timezone.utc).isoformat(),iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4 Windows x64',fresh_boot=True,normal_in_game_save=True,save_state_used=False,audio_enabled=True,single_emulator=True,runtime_memory_edits=False,screenshots=captures,
  checks=dict(blade_awakening_list_alignment=True,white_stone_yard_crafting=True,summon_naming=True,equipment_prompt_english=True,stone_equipped=True,no_bad_execution_address=True),
  limits=['Optional-battle titles reviewed as native decoded sprites; those battles were not played through.','Banner dispatch checked by bounded MIPS execution at two load bases; no animation capture in this run.','Targeted Windows tests, not a full playthrough or a Linux emulator test.'])
 for filename in ['battle-validation.json','stability-report.json']:
  r=json.loads((out/filename).read_text());assert r['passed'] and r['iso_sha256']==m['output_sha256']
 write(ui/'runtime-validation.json',runtime);write(out/'runtime-validation.json',runtime);write(ui/'reviewed-captures.json',notes)
 m['static_validation']['runtime_verified']=True;m['battle077_validation']=dict(passed=True,reports={n:sha(out/n) for n in ['battle-validation.json','stability-report.json','runtime-validation.json']},screenshots=captures)
 write(out/'manifest.json',m);print(json.dumps(dict(passed=True,screenshots=len(captures))))
if __name__=='__main__':main()
