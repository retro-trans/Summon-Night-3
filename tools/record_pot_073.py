"""Record reviewed fresh-boot Yard/Neutral-pot gameplay evidence."""
import json,hashlib
from datetime import datetime,timezone
from sn3_archive import ROOT
from pot_runtime_073 import client
def main():
 folder=ROOT/'work/output/0.1.73';ui=ROOT/'work/ui/pot_0.1.73/pot073-final';qa=ROOT/'work/scratch/pot073-final'
 manifest=json.loads((folder/'manifest.json').read_text());session=json.loads((qa/'session.json').read_text('utf-8-sig'))
 assert session['fresh_boot'] and not session['save_state_used'] and session['audio_enabled']
 assert session['iso']==str(folder/'Summon_Night_3_EN_0.1.73.iso')
 stability=json.loads((folder/'stability-report.json').read_text());assert stability['passed'] and stability['iso_sha256']==manifest['output_sha256']
 cache=json.loads((folder/'loaded-cache-validation.json').read_text());assert cache['all_loaded_bindings_valid'] and cache['names_terminated']
 request=client(19421);cpu=request('cpu.status');assert cpu['stepping'] and cpu['pc']==144800668
 log=(qa/'runtime.log').read_text();assert 'Bad execution access' not in log and 'E[MEMMAP]' not in log
 config=(qa/'strict.ini').read_text('utf-8-sig');assert 'IgnoreBadMemAccess=False' in config and '[Sound]\nEnable=True' in config
 evidence=[]
 for name in ['room','white_selected','white_created','name_yes','summon_spell','equip_select','reopen','next_unit']:
  path=ui/(name+'.png');meta=json.loads(path.with_suffix('.json').read_text())
  assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['png_sha256']
  evidence.append(dict(capture=str(path.relative_to(ROOT)).replace('\\','/'),png_sha256=meta['png_sha256']))
 report=dict(version='0.1.73',passed=True,created_at_utc=datetime.now(timezone.utc).isoformat(),
  iso_sha256=manifest['output_sha256'],emulator='PPSSPP 1.20.4 Windows x64',cpu_core='JIT',renderer='software',
  audio_enabled=True,ignore_bad_memory_access=False,fresh_boot=True,save_state_used=False,runtime_memory_edits=False,
  save='Private copy of supplied Chapter 2 normal save',combination=['Yard','All-Purpose Pot','white Neutral Summonite Stone'],
  checks=dict(created_summon=True,naming_completed=True,equipped_summon=True,spell_used='Random Hit',
   target='Yard (legal self-target in isolated QA)',mp_before=73,mp_after_crafting=68,mp_after_spell=53,
   hp_before=66,hp_after_spell=52,subsequent_unit_menu=True,no_bad_execution_address=True),
  loaded_cache=cache,evidence=evidence,limits=['Windows emulator run; supplied Linux host is not directly tested.','This targeted check is not a full playthrough.'])
 (folder/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(passed=True,version=report['version'],evidence_captures=len(evidence),spell=report['checks']['spell_used'])))
if __name__=='__main__':main()
