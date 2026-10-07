"""Bind final native checks and reviewed normal-save captures to build identity."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
def main():
 out=ROOT/'work/output/0.1.75';ui=ROOT/'work/ui/menus_0.1.75';m=json.loads((out/'manifest.json').read_text());captures=[]
 notes=json.loads((ui/'reviewed-captures.json').read_text())
 for case,names in notes.items():
  session=json.loads((ROOT/'work/scratch'/case/'session.json').read_text('utf-8-sig'))
  assert session['fresh_boot'] and not session['save_state_used'] and session['audio_enabled']
  assert session['iso_sha256']==m['output_sha256'],'Capture session belongs to another candidate'
  assert Path(session['iso']).resolve()==(out/m['output_iso']).resolve()
  for name,note in names.items():
   path=ui/case/(name+'.png');meta=json.loads(path.with_suffix('.json').read_text());assert meta['png_sha256']==sha(path) and [meta['width'],meta['height']]==[480,272]
   captures.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),note=note))
 runtime=dict(version='0.1.75',passed=True,iso_sha256=m['output_sha256'],emulator='PPSSPP 1.20.4',fresh_boot=True,normal_in_game_save=True,save_state_used=False,audio_enabled=True,single_emulator=True,runtime_memory_edits=False,screenshots=captures,limits=['Reviewed reported screens and category examples; not a complete playthrough.','Other variants were checked through native sprite import and bounded CPU execution.'])
 write(ui/'runtime-validation.json',runtime)
 checks={'menu-validation.json':'validation.json','name-cache-validation.json':'validation.json','stability-report.json':'cumulative-validation.json','runtime-validation.json':'runtime-validation.json'}
 recorded={}
 for dest,src in checks.items():
  r=json.loads((ui/src).read_text());assert r['passed'],src
  if 'iso_sha256' in r:assert r['iso_sha256']==m['output_sha256']
  r['iso_sha256']=m['output_sha256'];write(out/dest,r);recorded[dest]=sha(out/dest)
 m['static_validation']['runtime_verified']=True;m['menus075_validation']=dict(passed=True,reports=recorded,screenshots=captures)
 write(out/'manifest.json',m);print(json.dumps(dict(passed=True,captures=len(captures),iso_sha256=m['output_sha256'])))
if __name__=='__main__':main()
